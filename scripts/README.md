The model is trained automatically by the backend if no saved model exists.

For a manual training run:

```bash
cd backend
python -c "from app.services.ml import train_heart_model; print(train_heart_model())"
```

The trainer first tries the UCI Cleveland source documented by the project. If network access is unavailable, it uses a deterministic demo fallback so the application can still run.
