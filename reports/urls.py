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
    # Customer Loyalty Analytics
    CustomerLoyaltyDashboardView,
    CustomerLoyaltyListView,
    RepeatCustomersReportView,
    FrequencyReportView,
    RecencyReportView,
    LifetimeValueReportView,
    CohortRetentionReportView,
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
    # Customer Loyalty Analytics
    path('loyalty/dashboard/', CustomerLoyaltyDashboardView.as_view(), name='loyalty-dashboard'),
    path('loyalty/customers/', CustomerLoyaltyListView.as_view(), name='loyalty-customers'),
    path('loyalty/repeat/', RepeatCustomersReportView.as_view(), name='loyalty-repeat'),
    path('loyalty/frequency/', FrequencyReportView.as_view(), name='loyalty-frequency'),
    path('loyalty/recency/', RecencyReportView.as_view(), name='loyalty-recency'),
    path('loyalty/ltv/', LifetimeValueReportView.as_view(), name='loyalty-ltv'),
    path('loyalty/cohorts/', CohortRetentionReportView.as_view(), name='loyalty-cohorts'),
]
