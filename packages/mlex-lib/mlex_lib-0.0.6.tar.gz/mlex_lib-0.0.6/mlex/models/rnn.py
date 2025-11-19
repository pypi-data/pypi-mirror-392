import torch.nn as nn
import torch
import numpy as np
import time
from sklearn.base import BaseEstimator, ClassifierMixin
from sklearn.pipeline import Pipeline
from mlex.models.base_components.rnn_base_model import RNNBaseModel
from mlex.utils.preprocessing import PreProcessingTransformer
from mlex.utils.split import FeatureStratifiedSplit, PastFutureSplit
from mlex.utils.context_aware import ContextAware


class RNN(nn.Module, BaseEstimator, ClassifierMixin):
    def __init__(self, target_column, categories, timestamp_column, context_column=None,
                 val_split=0.3, split_stratify_column=None, sort_columns=None, **kwargs):
        """
        Initialize RNN model.
        
        Args:
            target_column: str - name of target column in dataset
            categories: list - categorical column values for preprocessing
            timestamp_column: str - timestamp column for context-aware sorting
            context_column: str - column to use for context-aware sorting (optional)
            val_split: float - validation split proportion (default 0.3)
            split_stratify_column: str - column to stratify validation split on (optional)
            sort_columns: optional explicit list of columns to sort by.
                          If provided it will be used as-is (must exist in X after
                          CONTEXT column is added). Otherwise defaults to ['CONTEXT', timestamp_column].
            **kwargs: additional model parameters
        """
        super().__init__()
        self.model_params = {
            'input_size': kwargs.get('input_size', None),
            'hidden_size': kwargs.get('hidden_size', None),
            'num_layers': kwargs.get('num_layers', None),
            'output_size': kwargs.get('output_size', None),
            'seq_length': kwargs.get('seq_length', None),
            'batch_size': kwargs.get('batch_size', None),
            'shuffle_dataloader': kwargs.get('shuffle_dataloader', None),
            'learning_rate': kwargs.get('learning_rate', None),
            'alpha': kwargs.get('alpha', None),
            'eps': kwargs.get('eps', None),
            'weight_decay': kwargs.get('weight_decay', None),
            'epochs': kwargs.get('epochs', None),
            'patience': kwargs.get('patience', None),
            'group_index': kwargs.get('group_index', None),
            'random_seed': kwargs.get('random_seed', None),
            'feature_names': kwargs.get('feature_names', None),
            'device': kwargs.get('device', None),
        }
        self.preprocessor_params = {
            'numeric_features': kwargs.get('numeric_features', None) or None,
            'categorical_features': kwargs.get('categorical_features', None) or None,
            'passthrough_features': kwargs.get('passthrough_features', None) or None,
            'context_feature': kwargs.get('context_feature', ['CONTEXT']) or ['CONTEXT'],
        }
        self.target_column = target_column
        self.categories = categories
        self.val_split = val_split
        self.split_stratify_column = split_stratify_column
        self.context_column = context_column
        self.timestamp_column = timestamp_column
        self.sort_columns = sort_columns
        self.fitted_ = False
        self.final_model = None
        self.model = None

        if self.model_params['input_size'] is not None:
            self.model = self._build_model()

        self.last_fit_time = 0

    @property
    def name(self):
        return 'RNN'

    def fit(self, X, y, **kwargs):
        self.model_params.update({key: kwargs[key] for key in list(self.model_params.keys()) if key in kwargs})
        self.preprocessor_params.update({key: kwargs[key] for key in list(self.preprocessor_params.keys()) if key in kwargs})

        X, y = self._apply_context_aware_transform(X, y)

        if self.split_stratify_column is not None:
            splitter = FeatureStratifiedSplit(
                stratify_column=self.split_stratify_column,
                split_proportion=self.val_split
            )
            splitter.fit(X, y)
            X_train, y_train, X_val, y_val = splitter.transform(X, y)
        else:
            splitter = PastFutureSplit(proportion=self.val_split, timestamp_column=self.timestamp_column)
            splitter.fit(X, y)
            X_train, y_train, X_val, y_val = splitter.transform(X, y)

        if self.model_params['input_size'] is None:
            preprocessor = PreProcessingTransformer(
                target_column=[self.target_column], 
                **{k: v for k, v in self.preprocessor_params.items()}, 
                categories=self.categories, 
                handle_unknown='ignore'
            )
            preprocessor.fit(X_train)
            self.model_params['feature_names'] = preprocessor.get_feature_names_out()
            self.model_params['input_size'] = self.model_params['feature_names'].shape[0] - 1

            X_val_transformed, y_val_transformed = preprocessor.transform(X_val, y_val)
            self.model_params['validation_data'] = (X_val_transformed, y_val_transformed)

            self.model = self._build_model()

        start = time.perf_counter()
        self.model.fit(X_train, y_train)
        end = time.perf_counter()
        
        self.last_fit_time = end - start
        self.fitted_ = True
        return self

    def predict(self, X):
        self._validate_fitted()

        X_sorted = self._sort_by_context(X)
        X_transformed = self._preprocess_features(X_sorted)

        windows, end_positions = self._build_sequence_windows(X_sorted, X_transformed)
        if len(windows) == 0:
            return np.zeros(len(X))

        seq_scores = self._predict_sequences(windows)
        y_pred_sorted = self._assemble_sorted_predictions(X_sorted, end_positions, seq_scores)

        return self._map_to_original_order(X, X_sorted, y_pred_sorted)

    def _apply_context_aware_transform(self, X, y=None):

        if self.timestamp_column is not None:
            context_sorter = ContextAware(
                target_column=self.target_column,
                timestamp_column=self.timestamp_column,
                context_column=self.context_column,
                sort_columns=self.sort_columns
            )
            X, y = context_sorter.transform(X, y)

        return X, y

    def _validate_fitted(self):
        if not self.fitted_:
            raise ValueError("Model is not fitted")

    def _sort_by_context(self, X):
        X_sorted, _ = self._apply_context_aware_transform(X.copy(), None)
        return X_sorted

    def _preprocess_features(self, X_sorted):
        preprocessor = self.model.named_steps['preprocessor']
        return preprocessor.transform(X_sorted)

    def _build_sequence_windows(self, X_sorted, X_transformed):
        seq_len = int(self.model_params.get('seq_length', 30) or 30)
        X_transformed = np.asarray(X_transformed)

        if self.context_column is None:
            groups = [list(range(len(X_sorted)))]
        else:
            groups = [list(idxs) for idxs in X_sorted.groupby(self.context_column).groups.values()]

        windows = []
        end_positions = []

        for group_idxs in groups:
            if len(group_idxs) < seq_len:
                continue
            for i in range(seq_len - 1, len(group_idxs)):
                start_pos = group_idxs[i - seq_len + 1]
                end_pos = group_idxs[i]

                window = X_transformed[start_pos:end_pos + 1, :-1]

                windows.append(window)
                end_positions.append(end_pos)

        return windows, end_positions

    def _predict_sequences(self, windows):
        seq_array = np.stack(windows).astype('float32')
        x_tensor = torch.from_numpy(seq_array).to(self.final_model.device)

        with torch.no_grad():
            return self.final_model.predict_proba(x_tensor).flatten()

    def _assemble_sorted_predictions(self, X_sorted, end_positions, seq_scores):
        y_pred = np.zeros(len(X_sorted), dtype=float)
        y_pred[np.array(end_positions, dtype=int)] = seq_scores
        return y_pred

    def _map_to_original_order(self, X_original, X_sorted, y_pred_sorted):
        orig_indices = X_sorted['__orig_index'].values
        index_to_position = {idx: pos for pos, idx in enumerate(X_original.index)}

        y_pred = np.zeros(len(X_original), dtype=float)
        for sorted_pos, orig_idx in enumerate(orig_indices):
            if orig_idx in index_to_position:
                y_pred[index_to_position[orig_idx]] = y_pred_sorted[sorted_pos]

        return y_pred

    def _build_model(self):
        model_params = {
            'input_size': self.model_params.get('input_size', 10) or 10,
            'hidden_size': self.model_params.get('hidden_size', 10) or 10,
            'num_layers': self.model_params.get('num_layers', 1) or 1,
            'output_size': self.model_params.get('output_size', 1) or 1,
            'seq_length': self.model_params.get('seq_length', 30) or 30,
            'batch_size': self.model_params.get('batch_size', 32) or 32,
            'shuffle_dataloader': self.model_params.get('shuffle_dataloader', True) if self.model_params.get('shuffle_dataloader') is not None else True,
            'learning_rate': self.model_params.get('learning_rate', 1e-3) or 1e-3,
            'alpha': self.model_params.get('alpha', .9) or .9,
            'eps': self.model_params.get('eps', 1e-7) or 1e-7,
            'weight_decay': self.model_params.get('weight_decay', 0.0) or 0.0,
            'epochs': self.model_params.get('epochs', 30) or 30,
            'patience': self.model_params.get('patience', 5) or 5,
            'group_index': self.model_params.get('group_index', -1) or -1,
            'random_seed': self.model_params.get('random_seed', None),
            'device': self.model_params.get('device', None),
            'validation_data': self.model_params.get('validation_data', None),
        }
        preprocessor_params = {
            'numeric_features': self.preprocessor_params.get('numeric_features', None) or None,
            'categorical_features': self.preprocessor_params.get('categorical_features', None) or None,
            'passthrough_features': self.preprocessor_params.get('passthrough_features', None) or None,
            'context_feature': self.preprocessor_params.get('context_feature', ['CONTEXT']) or ['CONTEXT'],
        }
        self.model_params.update(model_params)
        self.preprocessor_params.update(preprocessor_params)

        preprocessor = PreProcessingTransformer(
            target_column=[self.target_column], 
            **{k: v for k, v in preprocessor_params.items()}, 
            categories=self.categories, 
            handle_unknown='ignore'
        )
        self.final_model = RNNBaseModel(
            validation_data=model_params['validation_data'], 
            **{k: v for k, v in model_params.items() if k != 'validation_data'}
        )
        model = Pipeline(steps=[
            ('preprocessor', preprocessor),
            ('final_model', self.final_model)
        ])

        return model

    def get_feature_names(self):
        return self.model_params.get('feature_names')

    def get_params(self, deep=True):
        params = {**self.model_params, **self.preprocessor_params}.copy()
        params['target_column'] = self.target_column
        params['categories'] = self.categories
        params['split_stratify_column'] = self.split_stratify_column
        params['val_split'] = self.val_split
        params['context_column'] = self.context_column
        params['timestamp_column'] = self.timestamp_column
        params['sort_columns'] = self.sort_columns
        return params

    def set_params(self, **parameters):
        if 'target_column' in parameters:
            self.target_column = parameters.pop('target_column')
        if 'categories' in parameters:
            self.categories = parameters.pop('categories')
        if 'split_stratify_column' in parameters:
            self.split_stratify_column = parameters.pop('split_stratify_column')
        if 'val_split' in parameters:
            self.val_split = parameters.pop('val_split')
        if 'context_column' in parameters:
            self.context_column = parameters.pop('context_column')
        if 'timestamp_column' in parameters:
            self.timestamp_column = parameters.pop('timestamp_column')
        if 'sort_columns' in parameters:
            self.sort_columns = parameters.pop('sort_columns')

        self.model_params.update({key: parameters[key] for key in list(self.model_params.keys()) if key in parameters})
        self.preprocessor_params.update({key: parameters[key] for key in list(self.preprocessor_params.keys()) if key in parameters})
        return self

    def create_test_loader(self, X, y):
        self._validate_fitted()
        X, y = self._apply_context_aware_transform(X, y)

        X = self.model.named_steps['preprocessor'].transform(X)
        return self.final_model._create_dataloader(X, y, shuffle_dataloader=False)

    def get_y_true_sequences(self, X, y):
        self._validate_fitted()
        return y.values.flatten()
