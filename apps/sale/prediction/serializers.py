from rest_framework import serializers


class SalesPredictionSerializer(serializers.Serializer):
    product_id = serializers.IntegerField(
        required=False,
        allow_null=True,
        help_text="ID del producto para el cual predecir ventas. Si no se especifica, se predicen todas las ventas.",
    )
    days_ahead = serializers.IntegerField(
        default=30,
        min_value=1,
        max_value=365,
        help_text="Número de días hacia el futuro para predecir.",
    )
    time_unit = serializers.ChoiceField(
        choices=["day", "week", "month"],
        default="day",
        help_text="Unidad de tiempo para agrupar las predicciones.",
    )
    days_history = serializers.IntegerField(
        default=90,
        min_value=30,
        max_value=730,
        help_text="Cantidad de días históricos para entrenar el modelo.",
    )


class SalesPredictionResultSerializer(serializers.Serializer):
    date = serializers.DateField(help_text="Fecha de la predicción.")
    predicted_quantity = serializers.FloatField(
        help_text="Cantidad predicha de ventas."
    )
    product_id = serializers.IntegerField(
        required=False, allow_null=True, help_text="ID del producto."
    )
    product_name = serializers.CharField(
        required=False, allow_null=True, help_text="Nombre del producto."
    )
    predicted_sales = serializers.DecimalField(
        required=False,
        allow_null=True,
        max_digits=12,
        decimal_places=2,
        help_text="Venta predicha en dinero.",
    )
