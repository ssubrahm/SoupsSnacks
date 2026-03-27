from django.urls import path
from .views import (
    DashboardView,
    SalesReportView,
    CustomerReportView,
    ProductReportView,
    UnpaidOrdersReportView,
    InactiveCustomersReportView,
    OrderProfitabilityReportView,
    ExportSalesCSV,
    ExportCustomerCSV,
    ExportProductCSV,
    ExportUnpaidCSV,
)

urlpatterns = [
    path('dashboard/', DashboardView.as_view(), name='dashboard'),
    path('sales/', SalesReportView.as_view(), name='sales-report'),
    path('customers/', CustomerReportView.as_view(), name='customer-report'),
    path('products/', ProductReportView.as_view(), name='product-report'),
    path('unpaid/', UnpaidOrdersReportView.as_view(), name='unpaid-report'),
    path('inactive-customers/', InactiveCustomersReportView.as_view(), name='inactive-customers'),
    path('order-profitability/', OrderProfitabilityReportView.as_view(), name='order-profitability'),
    # CSV Exports
    path('export/sales/', ExportSalesCSV.as_view(), name='export-sales'),
    path('export/customers/', ExportCustomerCSV.as_view(), name='export-customers'),
    path('export/products/', ExportProductCSV.as_view(), name='export-products'),
    path('export/unpaid/', ExportUnpaidCSV.as_view(), name='export-unpaid'),
]
