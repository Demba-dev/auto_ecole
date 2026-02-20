from django.contrib import admin

# Register your models here.

from .models import Document

@admin.register(Document)
class DocumentAdmin(admin.ModelAdmin):
    list_filter = ('apprenant')
    list_display = ('type_document', 'date_upload', 'est_valide')
    list_filter = ('type_document', 'est_valide')
    search_fields = ('apprenant__nom', 'apprenant__prenom')
    raw_id_fields = ('apprenant',)
    ordering = ('-date_upload',)