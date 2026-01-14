from django.test import TestCase
from django.contrib.auth import get_user_model
from django.utils import timezone
from datetime import timedelta

from .models import Fournisseur, Contrat, Evaluation, Journal

User = get_user_model()


class FournisseurModelTest(TestCase):
    """Tests pour le modèle Fournisseur"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            email='test@example.com',
            password='testpass123'
        )
        self.fournisseur = Fournisseur.objects.create(
            nom='Test Fournisseur',
            categorie='fournitures',
            localisation='Abidjan',
            type='local',
            cree_par=self.user
        )
    
    def test_fournisseur_creation(self):
        """Test la création d'un fournisseur"""
        self.assertEqual(self.fournisseur.nom, 'Test Fournisseur')
        self.assertEqual(self.fournisseur.statut_conformite, 'en_attente')
    
    def test_documents_expires(self):
        """Test la détection des documents expirés"""
        yesterday = timezone.now().date() - timedelta(days=1)
        self.fournisseur.rib_date_expiration = yesterday
        self.fournisseur.save()
        
        documents_expires = self.fournisseur.documents_expires()
        self.assertIn('RIB', documents_expires)


class ContratModelTest(TestCase):
    """Tests pour le modèle Contrat"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            email='test@example.com',
            password='testpass123'
        )
        self.fournisseur = Fournisseur.objects.create(
            nom='Test Fournisseur',
            categorie='fournitures',
            localisation='Abidjan',
            type='local',
            cree_par=self.user
        )
        today = timezone.now().date()
        self.contrat = Contrat.objects.create(
            numero='CT-001',
            objet='Test Contrat',
            type='capex',
            montant=1000000,
            devise='XOF',
            date_signature=today,
            date_effet=today,
            date_echeance=today + timedelta(days=365),
            fournisseur=self.fournisseur,
            cree_par=self.user
        )
    
    def test_contrat_creation(self):
        """Test la création d'un contrat"""
        self.assertEqual(self.contrat.numero, 'CT-001')
        self.assertEqual(self.contrat.statut, 'en_attente')
    
    def test_jours_avant_echeance(self):
        """Test le calcul des jours avant échéance"""
        jours = self.contrat.jours_avant_echeance()
        self.assertAlmostEqual(jours, 365, delta=1)
    
    def test_est_a_renouveler(self):
        """Test la détection des contrats à renouveler"""
        # Contrat à 60 jours avant échéance
        today = timezone.now().date()
        self.contrat.date_echeance = today + timedelta(days=60)
        self.contrat.preavis = 90
        self.contrat.statut = 'actif'
        self.contrat.save()
        
        self.assertTrue(self.contrat.est_a_renouveler())


class EvaluationModelTest(TestCase):
    """Tests pour le modèle Évaluation"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            email='test@example.com',
            password='testpass123'
        )
        self.fournisseur = Fournisseur.objects.create(
            nom='Test Fournisseur',
            categorie='fournitures',
            localisation='Abidjan',
            type='local',
            cree_par=self.user
        )
        self.evaluation = Evaluation.objects.create(
            fournisseur=self.fournisseur,
            type_eval='post_livraison',
            note_qualite=85,
            note_delai=80,
            note_communication=90,
            note_conformite=88,
            note_innovation=75,
            cree_par=self.user
        )
    
    def test_evaluation_creation(self):
        """Test la création d'une évaluation"""
        self.assertEqual(self.evaluation.fournisseur.nom, 'Test Fournisseur')
    
    def test_calculer_score(self):
        """Test le calcul du score"""
        score = self.evaluation.calculer_score()
        # Score = 85*0.30 + 80*0.25 + 90*0.20 + 88*0.15 + 75*0.10 = 84.35
        self.assertAlmostEqual(score, 84.35, places=1)
        self.assertEqual(self.evaluation.mention, 'bon')
    
    def test_score_faible(self):
        """Test la détection d'un score faible"""
        evaluation = Evaluation.objects.create(
            fournisseur=self.fournisseur,
            type_eval='rfp',
            note_qualite=50,
            note_delai=55,
            note_communication=60,
            note_conformite=50,
            note_innovation=40,
            cree_par=self.user
        )
        score = evaluation.calculer_score()
        self.assertLess(score, 70)
        self.assertEqual(evaluation.mention, 'a_ameliorer')
