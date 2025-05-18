import pandas as pd
import numpy as np
import os
import pickle
import logging
from datetime import datetime, timedelta
from apps.sale.models import Sale
from apps.product.models import Product
from django.db.models import Sum, Count
from django.db.models.functions import TruncDay, TruncWeek, TruncMonth
from django.conf import settings
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LinearRegression

# Configurar logging
logger = logging.getLogger(__name__)


class SalesPredictor:
    MODELS_DIR = os.path.join(settings.BASE_DIR, "models", "sales_prediction")

    def __init__(self, company):
        self.company = company
        self.model = LinearRegression()
        self.scaler = StandardScaler()

        if not os.path.exists(self.MODELS_DIR):
            os.makedirs(self.MODELS_DIR, exist_ok=True)

    def _prepare_historical_data(self, product_id=None, days_back=90, time_unit="day"):
        start_date = datetime.now() - timedelta(days=days_back)

        total_company_sales = Sale.objects.filter(company=self.company).count()
        logger.info(
            f"Total de ventas para la compañía {self.company.id}: {total_company_sales}"
        )

        sales_query = Sale.objects.filter(company=self.company, date__gte=start_date)
        recent_sales_count = sales_query.count()
        logger.info(f"Ventas en los últimos {days_back} días: {recent_sales_count}")

        if product_id:
            sales_query = sales_query.filter(product_id=product_id)
            product_sales_count = sales_query.count()
            logger.info(f"Ventas para el producto {product_id}: {product_sales_count}")

        if time_unit == "day":
            trunc_function = TruncDay("date")
        elif time_unit == "week":
            trunc_function = TruncWeek("date")
        else:
            trunc_function = TruncMonth("date")

        sales_data = (
            sales_query.annotate(period=trunc_function)
            .values("period")
            .annotate(quantity=Sum("quantity"), total_sales=Sum("total_price"))
            .order_by("period")
        )

        periods_count = len(sales_data)
        logger.info(f"Períodos distintos con ventas: {periods_count} {time_unit}s")
        logger.info(f"Se requieren al menos 3 períodos distintos con ventas")
        if not sales_data:
            logger.warning("No se encontraron datos agrupados por período")
            return None

        df = pd.DataFrame(list(sales_data))
        df["day_of_week"] = df["period"].apply(lambda x: x.weekday())
        df["day_of_month"] = df["period"].apply(lambda x: x.day)
        df["month"] = df["period"].apply(lambda x: x.month)
        df["is_weekend"] = df["day_of_week"].apply(lambda x: 1 if x >= 5 else 0)

        logger.info(f"DataFrame creado con éxito, tamaño: {df.shape}")
        return df

    def train_model(self, product_id=None, days_back=90, time_unit="day"):
        logger.info(
            f"Iniciando entrenamiento del modelo para company_id={self.company.id}, product_id={product_id}"
        )

        df = self._prepare_historical_data(product_id, days_back, time_unit)

        if df is None or len(df) < 3:
            logger.warning(
                f"Datos insuficientes para entrenar el modelo: {df is None and 'None' or len(df)} puntos de datos (mínimo 3)"
            )
            from django.db import connection

            # Registrar la última consulta SQL ejecutada para depuración
            logger.info(
                f"Última consulta SQL: {connection.queries[-1]['sql'] if connection.queries else 'No hay consultas SQL registradas'}"
            )
            return False

        X = df[["day_of_week", "day_of_month", "month", "is_weekend"]]
        y = df["quantity"]

        X_scaled = self.scaler.fit_transform(X)

        self.model.fit(X_scaled, y)
        return True

    def _get_model_path(self, product_id=None, time_unit="day"):
        prefix = f"company_{self.company.id}"
        if product_id:
            prefix += f"_product_{product_id}"
        return os.path.join(self.MODELS_DIR, f"{prefix}_{time_unit}_model.pkl")

    def load_model(self, product_id=None, time_unit="day"):
        model_path = self._get_model_path(product_id, time_unit)
        if os.path.exists(model_path):
            try:
                with open(model_path, "rb") as f:
                    model_data = pickle.load(f)
                    self.model = model_data["model"]
                    self.scaler = model_data["scaler"]
                    last_trained = model_data.get("last_trained")

                    if (
                        last_trained is None
                        or (datetime.now() - last_trained).days >= 1
                    ):
                        return False
                    return True
            except Exception:
                return False
        return False

    def save_model(self, product_id=None, time_unit="day"):
        if self.model is None or self.scaler is None:
            return False

        model_path = self._get_model_path(product_id, time_unit)
        model_data = {
            "model": self.model,
            "scaler": self.scaler,
            "last_trained": datetime.now(),
        }

        try:
            with open(model_path, "wb") as f:
                pickle.dump(model_data, f)
            return True
        except Exception:
            return False

    def predict_future_sales(self, product_id=None, days_ahead=30, time_unit="day"):
        model_loaded = self.load_model(product_id, time_unit)
        if not model_loaded:
            if not self.train_model(product_id, days_ahead * 3, time_unit):
                return []
            self.save_model(product_id, time_unit)
        future_dates = [
            datetime.now() + timedelta(days=i) for i in range(1, days_ahead + 1)
        ]

        future_features = []
        for date in future_dates:
            feature = [
                date.weekday(),
                date.day,
                date.month,
                1 if date.weekday() >= 5 else 0,
            ]
            future_features.append(feature)

        future_features = np.array(future_features)
        future_features_scaled = self.scaler.transform(future_features)

        predictions = self.model.predict(future_features_scaled)

        results = []
        for i, date in enumerate(future_dates):
            predicted_quantity = max(0, round(float(predictions[i]), 2))

            result = {
                "date": date.strftime("%Y-%m-%d"),
                "predicted_quantity": predicted_quantity,
            }

            if product_id:
                try:
                    product = Product.objects.get(id=product_id)
                    result["product_id"] = product_id
                    result["product_name"] = product.name
                    result["predicted_sales"] = round(
                        predicted_quantity * float(product.price), 2
                    )
                except Product.DoesNotExist:
                    pass

            results.append(result)

        return results
