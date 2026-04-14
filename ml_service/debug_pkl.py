import pickle

try:
    with open('preprocessing_objects_rmsprop_optimized.pkl', 'rb') as f:
        data = pickle.load(f)
    print("Keys found in PKL:", list(data.keys()) if isinstance(data, dict) else "Not a dict")
    
    if isinstance(data, dict):
        for k, v in data.items():
            if hasattr(v, 'feature_names_in_'):
                print(f"{k} expects features:", list(v.feature_names_in_))
            elif getattr(v, 'categories_', None) is not None:
                print(f"{k} categories:", v.categories_)
except Exception as e:
    print("Error reading pkl:", e)
