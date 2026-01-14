from django.core.management.base import BaseCommand
from suppliers.models import Banque

class Command(BaseCommand):
    help = 'Peuple la base de données avec les 31 banques de Côte d\'Ivoire'

    def handle(self, *args, **kwargs):
        banques_data = [
            # Format: [nom, sigle, code_banque, code_bic]
            ['AFRILAND FIRST BANK', 'AFB', 'CI106', 'OMFNCIAB'],
            ['Banque Atlantique - Côte d\'Ivoire', 'BACI', 'CI034', 'ATCICIAB'],
            ['Bridge Bank Group Côte d\'Ivoire', 'BBG-CI', 'CI131', 'BGCDCIAB'],
            ['Banque D\'Abidjan', 'BDA', 'CI201', 'BDAJCIAB'],
            ['Banque de l\'Union Côte d\'Ivoire', 'BDU-CI', 'CI180', 'BDUTCIAB'],
            ['BGFIBANK COTE D\'IVOIRE', 'BGFI', 'CI162', 'BGFICIAB'],
            ['Banque de l\'Habitat de Côte d\'Ivoire', 'BHCI','CI068', 'BHCICIAB'],
            ['Banque Internationale pour le Commerce et l\'Industrie de la Côte d\'Ivoire', 'BICICI', 'CI006', 'BICICIAB'],
            ['Banque Malienne de Solidarité', 'BMS', '', 'BSOICIAB'],
            ['Banque Nationale d\'Investissement', 'BNI', 'CI092', 'CSSSCIAB'],
            ['Bank Of Africa - Côte d\'Ivoire', 'BOA', 'CI032', 'AFRICIAB'],
            ['Banque Sahélo-Saharienne pour l\'Investissement et le Commerce - Côte d\'Ivoire', 'BSIC-CI', 'CI154', 'BSAHCIAB'],
            ['CORIS BANK INTERNATIONALE', 'CBI-CI', 'CI166', 'CORICIAB'],
            ['CITIBANK Côte d\'Ivoire', 'CITIBANK', 'CI118', 'CITICIAX'],
            ['Banque Populaire de Côte d\'Ivoire', 'BPCI', 'CI155', 'BPCICICI'],
            ['Ecobank - Côte d\'Ivoire', 'ECOBANK-CI', 'CI059', 'ECOCICIAB'],
            ['Guaranty Trust Bank Côte d\'Ivoire', 'GTBANK-CI', 'CI163', 'GTBICIAB'],
            ['MANSA BANK', 'MANSA', 'CI211', 'MNSACIAB'],
            ['NSIA BANQUE', 'NSIA', 'CI042', 'BIAOCIAB'],
            ['Orange Bank Africa', 'OBA', 'CI214', 'ORACCIAB'],
            ['ORABANK Côte d\'Ivoire', 'ORA', 'CI121', 'ORBKCIAB'],
            ['Standard Chartered Bank Côte d\'Ivoire', 'SCBCI', 'CI097', 'SCBLCIAB'],
            ['Société Générale Côte d\'Ivoire', 'SGBCI', 'CI008', 'SGCICIAB'],
            ['Société Ivoirienne de Banque', 'SIB', 'CI007', 'SIVBCIAB'],
            ['Stanbic Bank Côte d\'Ivoire', 'STANBIC', 'CI190', 'SBICCIAB'],
            ['United Bank for Africa Côte d\'Ivoire', 'UBA', 'CI150', 'UNAFCIAB'],
            ['VERSUS BANK S.A.', 'VERSUS', 'CI112', 'VSBKCIAB'],
        ]
        
        count = 0
        for banque_info in banques_data:
            banque, created = Banque.objects.update_or_create(
                nom=banque_info[0],
                defaults={
                    'sigle': banque_info[1],
                    'code_banque': banque_info[2],
                    'code_bic': banque_info[3],
                    'iban_prefix': 'CI93'
                }
            )
            if created:
                count += 1
                self.stdout.write(self.style.SUCCESS(f'Banque créée: {banque.nom}'))
            else:
                self.stdout.write(self.style.SUCCESS(f'Banque mise à jour: {banque.nom}'))
        
        # Liste des noms de banques valides
        noms_valides = [b[0] for b in banques_data]
        noms_valides.append("AUTRE / BANQUE ETRANGERE") # Conserver cette entrée spéciale

        # Supprimer les banques qui ne sont pas dans la liste
        deleted_count, _ = Banque.objects.exclude(nom__in=noms_valides).delete()
        if deleted_count > 0:
             self.stdout.write(self.style.WARNING(f'{deleted_count} anciennes banques ont été supprimées.'))
        
        self.stdout.write(self.style.SUCCESS(f'Opération terminée.'))
