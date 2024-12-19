from django.core.management.base import BaseCommand
from web_backend.models import Product, Ad

class Command(BaseCommand):
    help = 'Synchronize promotion_price and is_featured fields for Products based on Ads'

    def handle(self, *args, **options):
        try:
            ads = Ad.objects.all()
            for ad in ads:
                # Lấy các sản phẩm liên kết với quảng cáo
                products = Product.objects.filter(productad__ad=ad)
                for product in products:
                    # Cập nhật giá khuyến mãi
                    if ad.discount_percentage:
                        product.promotion_price = product.price * (1 - ad.discount_percentage / 100)
                    
                    # Cập nhật is_featured
                    if product.promotion_price or product.ads.exists():
                        product.is_featured = True
                    else:
                        product.is_featured = False

                    # Lưu thay đổi
                    product.save()

            self.stdout.write(self.style.SUCCESS('Data synchronization completed successfully!'))

        except Exception as e:
            self.stderr.write(self.style.ERROR(f'Error during synchronization: {e}'))
