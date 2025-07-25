# Generated by Django 5.2.4 on 2025-07-25 13:43

import cloudinary.models
import django.core.validators
import django.db.models.deletion
import uuid
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Category',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100, unique=True)),
                ('slug', models.SlugField(max_length=100, unique=True)),
                ('description', models.TextField(blank=True)),
                ('icon', models.CharField(blank=True, help_text='Icon class or emoji', max_length=50)),
                ('is_active', models.BooleanField(default=True)),
                ('sort_order', models.PositiveIntegerField(default=0)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('parent', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='subcategories', to='listings.category')),
            ],
            options={
                'verbose_name': 'Category',
                'verbose_name_plural': 'Categories',
                'db_table': 'categories',
                'ordering': ['sort_order', 'name'],
            },
        ),
        migrations.CreateModel(
            name='Listing',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('title', models.CharField(max_length=200)),
                ('description', models.TextField()),
                ('price', models.DecimalField(decimal_places=2, max_digits=12, validators=[django.core.validators.MinValueValidator(0)])),
                ('currency', models.CharField(default='KES', max_length=3)),
                ('condition', models.CharField(choices=[('brand_new', 'Brand New'), ('like_new', 'Like New'), ('excellent', 'Excellent'), ('good', 'Good'), ('fair', 'Fair'), ('poor', 'Poor')], max_length=20)),
                ('location', models.CharField(choices=[('Baringo', 'Baringo'), ('Bomet', 'Bomet'), ('Bungoma', 'Bungoma'), ('Busia', 'Busia'), ('Elgeyo-Marakwet', 'Elgeyo-Marakwet'), ('Embu', 'Embu'), ('Garissa', 'Garissa'), ('Homa Bay', 'Homa Bay'), ('Isiolo', 'Isiolo'), ('Kajiado', 'Kajiado'), ('Kakamega', 'Kakamega'), ('Kericho', 'Kericho'), ('Kiambu', 'Kiambu'), ('Kilifi', 'Kilifi'), ('Kirinyaga', 'Kirinyaga'), ('Kisii', 'Kisii'), ('Kisumu', 'Kisumu'), ('Kitui', 'Kitui'), ('Kwale', 'Kwale'), ('Laikipia', 'Laikipia'), ('Lamu', 'Lamu'), ('Machakos', 'Machakos'), ('Makueni', 'Makueni'), ('Mandera', 'Mandera'), ('Marsabit', 'Marsabit'), ('Meru', 'Meru'), ('Migori', 'Migori'), ('Mombasa', 'Mombasa'), ("Murang'a", "Murang'a"), ('Nairobi', 'Nairobi'), ('Nakuru', 'Nakuru'), ('Nandi', 'Nandi'), ('Narok', 'Narok'), ('Nyamira', 'Nyamira'), ('Nyandarua', 'Nyandarua'), ('Nyeri', 'Nyeri'), ('Samburu', 'Samburu'), ('Siaya', 'Siaya'), ('Taita-Taveta', 'Taita-Taveta'), ('Tana River', 'Tana River'), ('Tharaka-Nithi', 'Tharaka-Nithi'), ('Trans Nzoia', 'Trans Nzoia'), ('Turkana', 'Turkana'), ('Uasin Gishu', 'Uasin Gishu'), ('Vihiga', 'Vihiga'), ('Wajir', 'Wajir'), ('West Pokot', 'West Pokot')], max_length=100)),
                ('delivery_options', models.CharField(choices=[('pickup_only', 'Pickup Only'), ('delivery_available', 'Delivery Available'), ('both', 'Both Pickup & Delivery')], max_length=20)),
                ('status', models.CharField(choices=[('draft', 'Draft'), ('active', 'Active'), ('expired', 'Expired'), ('sold', 'Sold'), ('suspended', 'Suspended')], default='draft', max_length=20)),
                ('is_premium', models.BooleanField(default=False)),
                ('is_featured', models.BooleanField(default=False)),
                ('is_hot_deal', models.BooleanField(default=False)),
                ('original_price', models.DecimalField(blank=True, decimal_places=2, max_digits=12, null=True)),
                ('discount_percentage', models.PositiveIntegerField(blank=True, null=True, validators=[django.core.validators.MinValueValidator(1), django.core.validators.MaxValueValidator(99)])),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('published_at', models.DateTimeField(blank=True, null=True)),
                ('expires_at', models.DateTimeField(blank=True, null=True)),
                ('views', models.PositiveIntegerField(default=0)),
                ('unique_views', models.PositiveIntegerField(default=0)),
                ('contact_count', models.PositiveIntegerField(default=0)),
                ('slug', models.SlugField(blank=True, max_length=250)),
                ('meta_description', models.CharField(blank=True, max_length=160)),
                ('category', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='listings', to='listings.category')),
                ('seller', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='listings', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'Listing',
                'verbose_name_plural': 'Listings',
                'db_table': 'listings',
                'ordering': ['-created_at'],
            },
        ),
        migrations.CreateModel(
            name='ListingContact',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('contact_type', models.CharField(choices=[('phone', 'Phone Call'), ('whatsapp', 'WhatsApp'), ('email', 'Email'), ('message', 'Direct Message')], max_length=20)),
                ('message', models.TextField(blank=True)),
                ('ip_address', models.GenericIPAddressField()),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('listing', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='contacts', to='listings.listing')),
                ('user', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='listing_contacts', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'Listing Contact',
                'verbose_name_plural': 'Listing Contacts',
                'db_table': 'listing_contacts',
            },
        ),
        migrations.CreateModel(
            name='ListingImage',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('image', cloudinary.models.CloudinaryField(max_length=255, verbose_name='listing_images')),
                ('alt_text', models.CharField(blank=True, max_length=200)),
                ('sort_order', models.PositiveIntegerField(default=0)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('listing', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='images', to='listings.listing')),
            ],
            options={
                'verbose_name': 'Listing Image',
                'verbose_name_plural': 'Listing Images',
                'db_table': 'listing_images',
                'ordering': ['sort_order', 'created_at'],
            },
        ),
        migrations.CreateModel(
            name='ListingReport',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('reason', models.CharField(choices=[('spam', 'Spam'), ('inappropriate', 'Inappropriate Content'), ('fake', 'Fake/Misleading'), ('duplicate', 'Duplicate Listing'), ('wrong_category', 'Wrong Category'), ('overpriced', 'Overpriced'), ('other', 'Other')], max_length=20)),
                ('description', models.TextField(blank=True)),
                ('is_resolved', models.BooleanField(default=False)),
                ('admin_notes', models.TextField(blank=True)),
                ('resolved_at', models.DateTimeField(blank=True, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('listing', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='reports', to='listings.listing')),
                ('reporter', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='listing_reports', to=settings.AUTH_USER_MODEL)),
                ('resolved_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='resolved_reports', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'Listing Report',
                'verbose_name_plural': 'Listing Reports',
                'db_table': 'listing_reports',
            },
        ),
        migrations.CreateModel(
            name='ListingView',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('ip_address', models.GenericIPAddressField()),
                ('user_agent', models.TextField(blank=True)),
                ('referrer', models.URLField(blank=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('listing', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='view_records', to='listings.listing')),
                ('user', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='listing_views', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'Listing View',
                'verbose_name_plural': 'Listing Views',
                'db_table': 'listing_views',
            },
        ),
        migrations.AddIndex(
            model_name='category',
            index=models.Index(fields=['slug'], name='categories_slug_b4303a_idx'),
        ),
        migrations.AddIndex(
            model_name='category',
            index=models.Index(fields=['is_active'], name='categories_is_acti_aae090_idx'),
        ),
        migrations.AddIndex(
            model_name='listing',
            index=models.Index(fields=['status', 'is_premium'], name='listings_status_4063e0_idx'),
        ),
        migrations.AddIndex(
            model_name='listing',
            index=models.Index(fields=['category', 'status'], name='listings_categor_7f7673_idx'),
        ),
        migrations.AddIndex(
            model_name='listing',
            index=models.Index(fields=['location', 'status'], name='listings_locatio_7d368f_idx'),
        ),
        migrations.AddIndex(
            model_name='listing',
            index=models.Index(fields=['seller', 'status'], name='listings_seller__9c3ec9_idx'),
        ),
        migrations.AddIndex(
            model_name='listing',
            index=models.Index(fields=['created_at'], name='listings_created_ac7d1b_idx'),
        ),
        migrations.AddIndex(
            model_name='listing',
            index=models.Index(fields=['expires_at'], name='listings_expires_96bc56_idx'),
        ),
        migrations.AddIndex(
            model_name='listing',
            index=models.Index(fields=['is_featured'], name='listings_is_feat_01aa9f_idx'),
        ),
        migrations.AddIndex(
            model_name='listing',
            index=models.Index(fields=['is_hot_deal'], name='listings_is_hot__fb38e4_idx'),
        ),
        migrations.AddIndex(
            model_name='listingcontact',
            index=models.Index(fields=['listing', 'created_at'], name='listing_con_listing_ce9d42_idx'),
        ),
        migrations.AddIndex(
            model_name='listingcontact',
            index=models.Index(fields=['user', 'created_at'], name='listing_con_user_id_606ce4_idx'),
        ),
        migrations.AddIndex(
            model_name='listingimage',
            index=models.Index(fields=['listing', 'sort_order'], name='listing_ima_listing_f22559_idx'),
        ),
        migrations.AddIndex(
            model_name='listingreport',
            index=models.Index(fields=['listing', 'is_resolved'], name='listing_rep_listing_88aeb1_idx'),
        ),
        migrations.AddIndex(
            model_name='listingreport',
            index=models.Index(fields=['reporter', 'created_at'], name='listing_rep_reporte_5121d6_idx'),
        ),
        migrations.AlterUniqueTogether(
            name='listingreport',
            unique_together={('listing', 'reporter')},
        ),
        migrations.AddIndex(
            model_name='listingview',
            index=models.Index(fields=['listing', 'created_at'], name='listing_vie_listing_5ee5fa_idx'),
        ),
        migrations.AddIndex(
            model_name='listingview',
            index=models.Index(fields=['user', 'created_at'], name='listing_vie_user_id_ec1445_idx'),
        ),
        migrations.AddIndex(
            model_name='listingview',
            index=models.Index(fields=['ip_address', 'created_at'], name='listing_vie_ip_addr_500046_idx'),
        ),
        migrations.AlterUniqueTogether(
            name='listingview',
            unique_together={('listing', 'user', 'ip_address')},
        ),
    ]
