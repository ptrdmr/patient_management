"""Lab results models definition."""

from django.db import models
from ..base import BasePatientModel


class CmpLabs(BasePatientModel):
    """Comprehensive Metabolic Panel (CMP) lab results."""

    sodium = models.DecimalField(max_digits=5, decimal_places=2)
    potassium = models.DecimalField(max_digits=5, decimal_places=2)
    chloride = models.DecimalField(max_digits=5, decimal_places=2)
    co2 = models.DecimalField(max_digits=5, decimal_places=2)
    glucose = models.DecimalField(max_digits=5, decimal_places=2)
    bun = models.DecimalField(max_digits=5, decimal_places=2)
    creatinine = models.DecimalField(max_digits=5, decimal_places=2)
    calcium = models.DecimalField(max_digits=5, decimal_places=2)
    protein = models.DecimalField(max_digits=5, decimal_places=2)
    albumin = models.DecimalField(max_digits=5, decimal_places=2)
    bilirubin = models.DecimalField(max_digits=5, decimal_places=2)
    gfr = models.DecimalField(max_digits=5, decimal_places=2)

    class Meta(BasePatientModel.Meta):
        verbose_name = "CMP Lab"
        verbose_name_plural = "CMP Labs"
        indexes = [
            *BasePatientModel.Meta.indexes,
            models.Index(fields=['sodium']),
            models.Index(fields=['potassium']),
            models.Index(fields=['glucose']),
            models.Index(fields=['creatinine'])
        ]

    def __str__(self):
        """Return string representation of CMP lab results."""
        return f"{self.patient} - CMP ({self.date})"


class CbcLabs(BasePatientModel):
    """Complete Blood Count (CBC) lab results."""

    rbc = models.DecimalField(max_digits=5, decimal_places=2)
    wbc = models.DecimalField(max_digits=5, decimal_places=2)
    hemoglobin = models.DecimalField(max_digits=5, decimal_places=2)
    hematocrit = models.DecimalField(max_digits=5, decimal_places=2)
    mcv = models.DecimalField(max_digits=5, decimal_places=2)
    mchc = models.DecimalField(max_digits=5, decimal_places=2)
    rdw = models.DecimalField(max_digits=5, decimal_places=2)
    platelets = models.DecimalField(max_digits=7, decimal_places=2)
    mch = models.DecimalField(max_digits=5, decimal_places=2)
    neutrophils = models.DecimalField(max_digits=5, decimal_places=2)
    lymphocytes = models.DecimalField(max_digits=5, decimal_places=2)
    monocytes = models.DecimalField(max_digits=5, decimal_places=2)
    eosinophils = models.DecimalField(max_digits=5, decimal_places=2)
    basophils = models.DecimalField(max_digits=5, decimal_places=2)

    class Meta(BasePatientModel.Meta):
        verbose_name = "CBC Lab"
        verbose_name_plural = "CBC Labs"
        indexes = [
            *BasePatientModel.Meta.indexes,
            models.Index(fields=['wbc']),
            models.Index(fields=['hemoglobin']),
            models.Index(fields=['platelets'])
        ]

    def __str__(self):
        """Return string representation of CBC lab results."""
        return f"{self.patient} - CBC ({self.date})" 