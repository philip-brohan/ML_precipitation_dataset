Fitting a decision-tree model with XGBoost
==========================================

The script fits an XGBoost regression model. The settings below describe the hyperparameters passed to XGBoost and the cross‑validation choices used to select the number of boosting rounds, together with the effect of changing each setting.

Hyperparameters
---------------

``objective``
  - Current: ``reg:squarederror``
  - Effect: Determines the loss optimized during training. Changing the objective (for example to a robust regression loss or a classification objective) changes what the model learns and can improve robustness to outliers or change the task.

``booster``
  - Current: ``gbtree``
  - Effect: Chooses the model family. ``gbtree`` builds decision trees and captures non‑linear interactions; ``gblinear`` fits a linear model that is faster for very high‑dimensional sparse data but cannot model non‑linear relationships.

``eta`` (learning rate)
  - Current: ``0.1``
  - Effect: Controls the step size at each boosting round. Smaller values (e.g. ``0.01``) slow convergence and generally improve generalization (but require more rounds); larger values (e.g. ``0.3`` or ``1``) speed training but increase risk of unstable convergence and overfitting.

``max_depth``
  - Current: ``10``
  - Effect: Maximum depth of each tree. Increasing depth allows modeling more complex interactions but raises overfitting risk; decreasing depth regularizes the model and reduces variance.

``subsample``
  - Current: ``0.8``
  - Effect: Fraction of training rows sampled per tree. Lower values add randomness, reduce overfitting and tree correlation, but increase bias; ``1.0`` disables row subsampling.

``colsample_bytree``
  - Current: ``0.8``
  - Effect: Fraction of features sampled per tree. Lower values reduce feature correlation across trees and help generalization when many features are irrelevant; higher values reduce bias but can increase overfitting.

``min_child_weight``
  - Current: ``50``
  - Effect: Minimum sum of instance weights (roughly a minimum leaf sample size). Larger values make trees more conservative (fewer, larger leaves) and reduce overfitting; smaller values allow small leaves and finer fits, increasing overfit risk on noisy data.

``lambda`` (L2 regularization)
  - Current: ``5.0``
  - Effect: L2 penalty on leaf weights. Larger values smooth predictions, reduce variance and combat overfitting; very large values can cause underfitting.

``alpha`` (L1 regularization)
  - Current: ``1.0``
  - Effect: L1 penalty on leaf weights. Encourages sparsity in learned weights and can improve robustness; increasing ``alpha`` increases sparsity and regularization.

``seed``
  - Current: ``42``
  - Effect: Controls randomness (fold splits, sampling). Changing the seed yields different stochastic realizations; keep it fixed for reproducibility or vary it for ensembles.

``verbosity``
  - Current: ``1``
  - Effect: Controls logging level. ``0`` is silent; higher values print more training diagnostics.

``tree_method``
  - Current: ``hist``
  - Effect: Chooses the tree construction algorithm. ``hist`` is efficient on CPU for large datasets; ``gpu_hist`` enables GPU acceleration if available; ``exact`` is more precise but much slower for large data.

Summary
-------
These hyperparameters trade off bias vs variance, speed vs accuracy, and CPU vs GPU usage. They interact: for example, reducing ``eta`` typically requires increasing allowed boosting rounds; stronger regularization (larger ``lambda``/``alpha`` or higher ``min_child_weight``) permits deeper trees without as much overfitting.

Cross‑validation specification
------------------------------

The script runs ``xgboost.cv`` on the training DMatrix to select the number of boosting rounds. Each option below is taken from the script and the effect of changing it is noted.

``params`` (passed through)
  - The same parameter dictionary used for training is used inside each CV fold; changing those parameters changes the learner behaviour and the CV‑estimated optimal number of rounds.

``num_boost_round``
  - Current: ``2000``
  - Effect: Upper bound on boosting rounds considered by CV. Larger values allow more rounds (useful with small ``eta``) but increase compute; with early stopping this acts as a safe maximum.

``nfold``
  - Current: ``5``
  - Effect: Number of CV folds. Increasing ``nfold`` (e.g. to 10) gives a more stable generalization estimate but multiplies compute; decreasing ``nfold`` speeds CV but reduces reliability. For temporally correlated data, standard k‑fold can leak information—use blocked or grouped CV instead.

``metrics``
  - Current: ``("rmse",)``
  - Effect: Metric(s) used to evaluate performance on each fold. Changing the metric (for example to MAE) changes which model/rounds are selected; pick a metric aligned with modeling goals.

``early_stopping_rounds``
  - Current: ``20``
  - Effect: Number of rounds without improvement on the test metric before CV stops. Larger values are more patient but cost more compute; smaller values stop earlier and save compute but risk premature stopping due to noise.

``as_pandas``
  - Current: ``True``
  - Effect: Returns CV results as a pandas DataFrame for easy inspection; setting ``False`` returns a dict.

``seed`` (for CV)
  - Current: ``42``
  - Effect: Controls randomness in fold assignment and sampling. Changing it yields different fold splits and possibly different best rounds.

CV result handling
  - The script sets ``best_rounds = int(cvres["test-rmse-mean"].idxmin() + 1)``.
  - Effect: Chooses the boosting round index with minimum test RMSE mean (zero‑based index + 1) for final training. You may prefer a more conservative selection (for example adding a safety margin or using a one‑standard‑error rule).

Notes and trade‑offs
  - CV gives an empirical choice of boosting rounds but increases computational cost versus a single validation set.
  - For time‑series or grouped data, use CV schemes that prevent leakage (time blocks, group folds) or use a held‑out validation set respecting the data structure.
  - Hyperparameter changes interact with CV: e.g. smaller ``eta`` increases required rounds and CV cost; stronger regularization often reduces the optimal number of rounds.
