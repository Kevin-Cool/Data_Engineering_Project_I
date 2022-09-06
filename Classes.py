class KMO:
  def __init__(self, _name, _age, _email, _telefoonNr,_webAdres,_personeelsbestanden,_wcm,_ibid,_beursnotatie,_duurzaamheid,_b2b):
    self.onderneminsNr = _name
    self.naam = _age
    self.email = _email
    self.telefoonNr = _telefoonNr
    self.webAdres = _webAdres
    self.personeelsbestanden = _personeelsbestanden
    self.wcm = _wcm
    self.ibid = _ibid
    self.beursnotatie = _beursnotatie
    self.duurzaamheid = _duurzaamheid
    self.b2b = _b2b
  
class Naturalcapital:
  def __init__(self):
    self.ID = 0
    self.energySourcesScore = 0
    self.energySourcesText = ""
    self.waterSourcesScore = 0
    self.waterSourcesText = ""
    self.greenhoussGasesScore = 0
    self.greenhoussGasesText = ""
    self.pollutingEmissionsScore = 0
    self.pollutingEmissionsText = ""
    self.environmentalImpactScore = 0
    self.environmentalImpactIText = ""
    self.impactHealthSafetyScore = 0
    self.impactHealthSafetyText = ""
    self.furtherRequirementsScore = 0
    self.furtherRequirementsText = ""
    self.environmentalPolicyScore = 0
    self.environmentalPolicyText = ""
    self.totalScore = 0
  
  def calculate_score(self):
    self.totalScore = self.energySourcesScore + self.waterSourcesScore + self.greenhoussGasesScore + self.pollutingEmissionsScore + self.environmentalImpactScore + self.impactHealthSafetyScore + self.furtherRequirementsScore + self.environmentalPolicyScore

class Humancapital:
  def __init__(self):
    self.ID = 0
    self.genderEqualityScore = 0
    self.genderEqualityText = ""
    self.workersRightsScore = 0
    self.workersRightsText = ""
    self.socialRelationshipsScore = 0
    self.socialRelationshipsText = ""
    self.employmentScore = 0
    self.employmentIText = ""
    self.organisationAtWorkScore = 0
    self.organisationAtWorkText = ""
    self.healthAndSafetyScore = 0
    self.healthAndSafetyIText = ""
    self.trainingPolicyScore = 0
    self.trainingPolicyText = ""
    self.totalScore = 0
  
  def calculate_score(self):
    self.totalScore = self.genderEqualityScore + self.workersRightsScore + self.socialRelationshipsScore + self.employmentScore + self.organisationAtWorkScore + self.healthAndSafetyScore + self.trainingPolicyScore 
     
    
    



