"""
cures.py
--------
Treatment and prevention info for every PlantVillage disease class.
Keys match the disease name returned by parse_label() in app.py.
"""

CURES = {
    # ── Apple ──────────────────────────────────────────────────────────────
    "Apple scab": {
        "cause":    "Fungal infection caused by Venturia inaequalis.",
        "symptoms": "Olive-green to brown scabby lesions on leaves and fruit.",
        "treatment": [
            "Apply fungicides (captan, myclobutanil) at bud break and repeat every 7–10 days.",
            "Remove and destroy fallen infected leaves to reduce spore load.",
            "Prune trees to improve air circulation.",
        ],
        "prevention": "Plant scab-resistant apple varieties. Avoid overhead irrigation.",
    },
    "Black rot": {
        "cause":    "Fungal pathogen Botryosphaeria obtusa.",
        "symptoms": "Brown circular lesions with purple borders on leaves; mummified fruit.",
        "treatment": [
            "Prune out dead or cankered wood and burn it.",
            "Apply captan or thiophanate-methyl fungicide during the growing season.",
            "Remove mummified fruit from the tree and ground.",
        ],
        "prevention": "Maintain tree vigor with proper fertilization. Avoid wounding bark.",
    },
    "Cedar apple rust": {
        "cause":    "Fungal pathogen Gymnosporangium juniperi-virginianae.",
        "symptoms": "Bright orange-yellow spots on upper leaf surface; tube-like structures below.",
        "treatment": [
            "Apply myclobutanil or propiconazole fungicide from pink bud stage through cover sprays.",
            "Remove nearby juniper/cedar trees if possible (alternate host).",
        ],
        "prevention": "Plant rust-resistant apple varieties. Create distance from cedar trees.",
    },

    # ── Blueberry / Cherry / Raspberry / Soybean / Squash (healthy or single disease) ──
    "Powdery mildew": {
        "cause":    "Various powdery mildew fungi (Podosphaera spp., Erysiphe spp.).",
        "symptoms": "White powdery coating on leaves, stems, and buds.",
        "treatment": [
            "Spray with potassium bicarbonate, neem oil, or sulfur-based fungicide.",
            "Remove heavily infected plant parts.",
            "Apply systemic fungicides (myclobutanil, trifloxystrobin) for severe cases.",
        ],
        "prevention": "Ensure good air circulation. Avoid excess nitrogen fertilizer.",
    },

    # ── Corn ───────────────────────────────────────────────────────────────
    "Cercospora leaf spot Gray leaf spot": {
        "cause":    "Fungal pathogen Cercospora zeae-maydis.",
        "symptoms": "Rectangular gray-tan lesions running parallel to leaf veins.",
        "treatment": [
            "Apply strobilurin or triazole fungicides (azoxystrobin, propiconazole) at tasseling.",
            "Rotate crops — avoid planting corn in the same field consecutively.",
            "Till crop residue to reduce overwintering spores.",
        ],
        "prevention": "Plant resistant hybrids. Practice crop rotation with non-host crops.",
    },
    "Common rust ": {
        "cause":    "Fungal pathogen Puccinia sorghi.",
        "symptoms": "Small, oval, brick-red pustules scattered on both leaf surfaces.",
        "treatment": [
            "Apply triazole fungicides (propiconazole, tebuconazole) at early rust detection.",
            "Scout fields regularly and act before disease spreads.",
        ],
        "prevention": "Plant rust-resistant corn hybrids. Early planting can reduce exposure.",
    },
    "Northern Leaf Blight": {
        "cause":    "Fungal pathogen Exserohilum turcicum.",
        "symptoms": "Long, cigar-shaped gray-green to tan lesions on leaves.",
        "treatment": [
            "Apply fungicides (azoxystrobin, pyraclostrobin) at early disease onset.",
            "Remove and destroy infected crop debris after harvest.",
        ],
        "prevention": "Use resistant hybrids. Rotate crops and till residue.",
    },

    # ── Grape ──────────────────────────────────────────────────────────────
    "Grape Black rot": {
        "cause":    "Fungal pathogen Guignardia bidwellii.",
        "symptoms": "Tan lesions with dark borders on leaves; shriveled black mummified berries.",
        "treatment": [
            "Apply myclobutanil or mancozeb fungicide from early shoot growth through veraison.",
            "Remove and destroy mummified berries and infected canes.",
            "Prune vines to open the canopy for better air flow.",
        ],
        "prevention": "Remove all mummies before bud break. Maintain open vine canopy.",
    },
    "Esca (Black Measles)": {
        "cause":    "Complex of wood-rotting fungi (Phaeomoniella, Phaeoacremonium spp.).",
        "symptoms": "Tiger-stripe leaf discoloration; dark streaking in wood; berry spotting.",
        "treatment": [
            "No fully effective chemical cure exists — focus on prevention.",
            "Prune infected wood well below visible symptoms.",
            "Protect pruning wounds immediately with fungicidal paste (thiophanate-methyl).",
        ],
        "prevention": "Prune during dry weather. Avoid large pruning wounds. Use certified planting material.",
    },
    "Leaf blight (Isariopsis Leaf Spot)": {
        "cause":    "Fungal pathogen Isariopsis clavispora (Pseudocercospora vitis).",
        "symptoms": "Irregular dark brown spots with yellow halos on older leaves.",
        "treatment": [
            "Apply copper-based fungicides or mancozeb at first sign of symptoms.",
            "Remove and destroy heavily infected leaves.",
        ],
        "prevention": "Ensure good canopy ventilation. Avoid wetting foliage during irrigation.",
    },

    # ── Orange ─────────────────────────────────────────────────────────────
    "Haunglongbing (Citrus greening)": {
        "cause":    "Bacterial pathogen Candidatus Liberibacter asiaticus, spread by Asian citrus psyllid.",
        "symptoms": "Yellow shoots, blotchy mottled leaves, lopsided bitter fruit.",
        "treatment": [
            "No cure exists — infected trees should be removed and destroyed.",
            "Control the Asian citrus psyllid vector with insecticides (imidacloprid, dimethoate).",
            "Inject antibiotics (oxytetracycline) to suppress symptoms temporarily.",
        ],
        "prevention": "Use certified disease-free nursery stock. Monitor and control psyllid populations.",
    },

    # ── Peach ──────────────────────────────────────────────────────────────
    "Bacterial spot": {
        "cause":    "Bacterium Xanthomonas arboricola pv. pruni.",
        "symptoms": "Water-soaked spots turning brown/purple on leaves; cracked lesions on fruit.",
        "treatment": [
            "Apply copper-based bactericides (copper hydroxide) from shuck split through harvest.",
            "Avoid overhead irrigation to reduce leaf wetness.",
            "Remove and destroy heavily infected plant material.",
        ],
        "prevention": "Plant resistant varieties. Avoid working in the orchard when foliage is wet.",
    },

    # ── Pepper ─────────────────────────────────────────────────────────────
    "Pepper Bacterial spot": {
        "cause":    "Bacterium Xanthomonas campestris pv. vesicatoria.",
        "symptoms": "Small water-soaked leaf spots turning brown with yellow halos; scabby fruit lesions.",
        "treatment": [
            "Apply copper bactericide + mancozeb mixture every 5–7 days during wet weather.",
            "Remove infected plant debris promptly.",
            "Avoid working among wet plants to prevent spread.",
        ],
        "prevention": "Use certified disease-free seed. Rotate crops. Plant resistant varieties.",
    },

    # ── Potato ─────────────────────────────────────────────────────────────
    "Early blight": {
        "cause":    "Fungal pathogen Alternaria solani.",
        "symptoms": "Dark brown concentric ring (target-board) lesions on older leaves.",
        "treatment": [
            "Apply chlorothalonil, mancozeb, or azoxystrobin fungicide at first symptom.",
            "Remove and destroy infected lower leaves.",
            "Ensure adequate potassium fertilization to boost plant resistance.",
        ],
        "prevention": "Use certified seed. Rotate crops. Avoid overhead watering.",
    },
    "Late blight": {
        "cause":    "Oomycete pathogen Phytophthora infestans.",
        "symptoms": "Water-soaked gray-green lesions with white mold on leaf undersides; rapid collapse.",
        "treatment": [
            "Apply metalaxyl, cymoxanil, or chlorothalonil fungicide immediately.",
            "Destroy infected plants — do NOT compost them.",
            "Hill up soil around potato stems to protect tubers.",
        ],
        "prevention": "Plant certified blight-free seed tubers. Use resistant varieties. Monitor weather forecasts.",
    },

    # ── Strawberry ─────────────────────────────────────────────────────────
    "Leaf scorch": {
        "cause":    "Fungal pathogen Diplocarpon earlianum.",
        "symptoms": "Small purple spots enlarging to irregular dark blotches; scorched appearance.",
        "treatment": [
            "Apply captan or myclobutanil fungicide at first sign of disease.",
            "Remove and destroy infected leaves.",
            "Renovate beds after harvest by mowing and thinning.",
        ],
        "prevention": "Plant resistant varieties. Avoid overhead irrigation. Ensure good air circulation.",
    },

    # ── Tomato ─────────────────────────────────────────────────────────────
    "Tomato Bacterial spot": {
        "cause":    "Bacterium Xanthomonas vesicatoria.",
        "symptoms": "Small dark water-soaked spots on leaves and fruit; yellow halos.",
        "treatment": [
            "Spray copper bactericide + mancozeb every 5–7 days.",
            "Remove infected plant parts and avoid working in wet conditions.",
        ],
        "prevention": "Use disease-free transplants. Rotate crops. Avoid overhead irrigation.",
    },
    "Tomato Early blight": {
        "cause":    "Fungal pathogen Alternaria solani.",
        "symptoms": "Dark concentric ring lesions on lower leaves; stem collar rot in seedlings.",
        "treatment": [
            "Apply chlorothalonil or mancozeb fungicide every 7–10 days.",
            "Remove infected lower leaves and improve air circulation.",
            "Mulch around plants to prevent soil splash.",
        ],
        "prevention": "Rotate crops. Use resistant varieties. Avoid wetting foliage.",
    },
    "Late blight": {
        "cause":    "Oomycete Phytophthora infestans.",
        "symptoms": "Greasy gray-green lesions; white sporulation on leaf undersides; rapid plant death.",
        "treatment": [
            "Apply metalaxyl or cymoxanil-based fungicide immediately.",
            "Remove and bag infected plants — do NOT compost.",
            "Spray remaining healthy plants preventively.",
        ],
        "prevention": "Plant resistant varieties. Avoid overhead watering. Scout regularly.",
    },
    "Leaf Mold": {
        "cause":    "Fungal pathogen Passalora fulva (Cladosporium fulvum).",
        "symptoms": "Pale green-yellow spots on upper leaf surface; olive-green mold below.",
        "treatment": [
            "Apply chlorothalonil, mancozeb, or copper fungicide.",
            "Reduce humidity in greenhouses by improving ventilation.",
            "Remove and destroy infected leaves.",
        ],
        "prevention": "Use resistant varieties. Keep humidity below 85%. Space plants well.",
    },
    "Septoria leaf spot": {
        "cause":    "Fungal pathogen Septoria lycopersici.",
        "symptoms": "Small circular spots with dark borders and gray centers; tiny black dots inside.",
        "treatment": [
            "Apply chlorothalonil, mancozeb, or copper fungicide every 7–10 days.",
            "Remove infected lower leaves immediately.",
            "Avoid overhead watering.",
        ],
        "prevention": "Rotate crops. Mulch soil. Use disease-free transplants.",
    },
    "Spider mites Two-spotted spider mite": {
        "cause":    "Pest: Tetranychus urticae (two-spotted spider mite).",
        "symptoms": "Stippled, bronzed leaves; fine webbing on undersides; leaf drop.",
        "treatment": [
            "Apply miticide (abamectin, bifenazate) or insecticidal soap.",
            "Spray forceful water jets on leaf undersides to dislodge mites.",
            "Introduce predatory mites (Phytoseiulus persimilis) for biological control.",
        ],
        "prevention": "Avoid water stress. Reduce dusty conditions. Monitor regularly.",
    },
    "Target Spot": {
        "cause":    "Fungal pathogen Corynespora cassiicola.",
        "symptoms": "Brown circular lesions with concentric rings and yellow halos.",
        "treatment": [
            "Apply azoxystrobin, chlorothalonil, or fluxapyroxad fungicide.",
            "Remove infected leaves and improve canopy airflow.",
        ],
        "prevention": "Rotate crops. Avoid dense planting. Use resistant varieties where available.",
    },
    "Tomato mosaic virus": {
        "cause":    "Tomato mosaic virus (ToMV) — mechanically transmitted.",
        "symptoms": "Mosaic light/dark green mottling on leaves; leaf distortion; stunted growth.",
        "treatment": [
            "No chemical cure — remove and destroy infected plants immediately.",
            "Disinfect tools with 10% bleach or 70% alcohol between plants.",
            "Wash hands thoroughly before handling plants.",
        ],
        "prevention": "Use virus-free certified seed. Plant resistant varieties. Control aphid vectors.",
    },
    "Tomato Yellow Leaf Curl Virus": {
        "cause":    "Tomato yellow leaf curl virus (TYLCV) — transmitted by whiteflies.",
        "symptoms": "Upward leaf curling, yellowing of leaf margins, stunted plants, flower drop.",
        "treatment": [
            "No cure — remove and destroy infected plants to prevent spread.",
            "Control whitefly populations with imidacloprid or thiamethoxam.",
            "Use yellow sticky traps to monitor and reduce whitefly numbers.",
        ],
        "prevention": "Use TYLCV-resistant varieties. Install insect-proof nets in greenhouses.",
    },
}

# Healthy message shown for all healthy classes
HEALTHY_MESSAGE = {
    "cause":     "No disease detected.",
    "symptoms":  "The leaf appears healthy with no visible signs of infection.",
    "treatment": ["Continue regular monitoring and good agricultural practices."],
    "prevention": "Maintain proper irrigation, fertilization, and field hygiene.",
}


def get_cure(disease: str) -> dict:
    """
    Look up cure info for a disease name.
    Tries exact match first, then partial match, then returns healthy message.
    """
    if "healthy" in disease.lower():
        return HEALTHY_MESSAGE

    # Exact match
    if disease in CURES:
        return CURES[disease]

    # Partial match (e.g. 'Early blight' matches 'Tomato Early blight')
    disease_lower = disease.lower()
    for key, val in CURES.items():
        if key.lower() in disease_lower or disease_lower in key.lower():
            return val

    # Fallback
    return {
        "cause":     "Specific cause data not available.",
        "symptoms":  disease,
        "treatment": ["Consult a local agronomist for targeted treatment advice."],
        "prevention": "Practice crop rotation, proper sanitation, and use certified seeds.",
    }
