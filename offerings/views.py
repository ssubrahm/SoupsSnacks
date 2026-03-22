from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.http import HttpResponse
from django.db.models import Q
from datetime import datetime
from .models import DailyOffering, DailyOfferingItem
from .serializers import (
    DailyOfferingSerializer,
    DailyOfferingListSerializer,
    DailyOfferingCreateUpdateSerializer
)
from accounts.permissions import IsOperator


class DailyOfferingViewSet(viewsets.ModelViewSet):
    queryset = DailyOffering.objects.all()
    permission_classes = [IsAuthenticated, IsOperator]
    
    def get_serializer_class(self):
        if self.action == 'list':
            # If filtering by specific date, return full serializer with items
            if self.request.query_params.get('date'):
                return DailyOfferingSerializer
            return DailyOfferingListSerializer
        elif self.action in ['create', 'update', 'partial_update']:
            return DailyOfferingCreateUpdateSerializer
        return DailyOfferingSerializer
    
    def get_queryset(self):
        queryset = DailyOffering.objects.all()
        
        # Filter by date
        date = self.request.query_params.get('date')
        if date:
            queryset = queryset.filter(offering_date=date)
        
        # Filter by date range
        start_date = self.request.query_params.get('start_date')
        end_date = self.request.query_params.get('end_date')
        if start_date:
            queryset = queryset.filter(offering_date__gte=start_date)
        if end_date:
            queryset = queryset.filter(offering_date__lte=end_date)
        
        # Filter by active status
        is_active = self.request.query_params.get('is_active')
        if is_active is not None:
            queryset = queryset.filter(is_active=is_active.lower() == 'true')
        
        return queryset
    
    @action(detail=False, methods=['get'])
    def stats(self, request):
        """Get offering statistics"""
        total = DailyOffering.objects.count()
        active = DailyOffering.objects.filter(is_active=True).count()
        inactive = total - active
        
        return Response({
            'total': total,
            'active': active,
            'inactive': inactive,
        })
    
    @action(detail=True, methods=['post'])
    def toggle_active(self, request, pk=None):
        """Toggle active status"""
        offering = self.get_object()
        offering.is_active = not offering.is_active
        offering.save()
        
        serializer = self.get_serializer(offering)
        return Response(serializer.data)
    
    @action(detail=True, methods=['get'])
    def export_text(self, request, pk=None):
        """Export offering as plain text for WhatsApp/Email/Google Forms"""
        offering = self.get_object()
        
        # Build text content
        lines = []
        lines.append(f"🍛 MENU FOR {offering.offering_date.strftime('%A, %B %d, %Y')}")
        lines.append("=" * 50)
        lines.append("")
        
        if offering.notes:
            lines.append(f"📝 {offering.notes}")
            lines.append("")
        
        # Group items by category
        items = offering.items.select_related('product').all()
        
        if not items:
            lines.append("No items available for this date.")
        else:
            # Group by category
            from collections import defaultdict
            by_category = defaultdict(list)
            
            for item in items:
                by_category[item.product.category].append(item)
            
            category_names = {
                'soups': '🍲 SOUPS',
                'snacks': '🥘 SNACKS',
                'sweets': '🍰 SWEETS',
                'lunch': '🍱 LUNCH',
                'dinner': '🍽️ DINNER',
                'pickle': '🥒 PICKLES',
                'combos': '🎁 COMBO MEALS',
                'other': '🍴 OTHER',
            }
            
            for category in ['soups', 'snacks', 'sweets', 'lunch', 'dinner', 'pickle', 'combos', 'other']:
                if category in by_category:
                    lines.append(category_names.get(category, category.upper()))
                    lines.append("-" * 50)
                    
                    for item in by_category[category]:
                        product = item.product
                        line = f"• {product.name} ({product.unit}) - ₹{product.selling_price}"
                        
                        if item.available_quantity is not None:
                            line += f" [Limited: {item.available_quantity} available]"
                        
                        lines.append(line)
                    
                    lines.append("")
        
        lines.append("=" * 50)
        lines.append("📱 To order, reply with item names and quantities")
        lines.append("🚚 Delivery available within Bangalore")
        lines.append("")
        lines.append("Thank you! 🙏")
        
        text_content = "\n".join(lines)
        
        # Return as downloadable text file
        response = HttpResponse(text_content, content_type='text/plain; charset=utf-8')
        filename = f"menu_{offering.offering_date.strftime('%Y%m%d')}.txt"
        response['Content-Disposition'] = f'attachment; filename="{filename}"'
        
        return response
    
    @action(detail=True, methods=['get'])
    def export_json(self, request, pk=None):
        """Export offering as JSON (for programmatic use)"""
        offering = self.get_object()
        serializer = DailyOfferingSerializer(offering)
        return Response(serializer.data)
