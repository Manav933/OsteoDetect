import requests
import json

from django.conf import settings
ML_SERVICE_URL = getattr(settings, 'ML_SERVICE_URL', 'http://127.0.0.1:8000')

class MLClient:
    @staticmethod
    def health_check():
        try:
            response = requests.get(f"{ML_SERVICE_URL}/health", timeout=2)
            if response.status_code != 200:
                return False
            payload = response.json()
            return bool(payload.get('status') == 'healthy' and payload.get('model_loaded'))
        except Exception:
            return False

    @staticmethod
    def predict(diagnosis_record):
        try:
            url = f"{ML_SERVICE_URL}/predict"
            
            # Prepare data
            structured_data = {
                "IDENTIFIER_1": diagnosis_record.identifier_1 or "",
                "SPINE_SCANDATE": str(diagnosis_record.spine_scandate) if diagnosis_record.spine_scandate else "",
                "SPINE_BMD": diagnosis_record.spine_bmd or 0.0,
                "SPINE_TSCORE": diagnosis_record.spine_tscore or 0.0,
                "HIP_SCANDATE": str(diagnosis_record.hip_scandate) if diagnosis_record.hip_scandate else "",
                "HIP_BMD": diagnosis_record.hip_bmd or 0.0,
                "HIP_TSCORE": diagnosis_record.hip_tscore or 0.0,
                "HIPNECK_SCANDATE": str(diagnosis_record.hipneck_scandate) if diagnosis_record.hipneck_scandate else "",
                "HIPNECK_BMD": diagnosis_record.hipneck_bmd or 0.0,
                "HIPNECK_TSCORE": diagnosis_record.hipneck_tscore or 0.0,
                "BIRTHDATE": str(diagnosis_record.birthdate) if diagnosis_record.birthdate else "",
                "AGE_CATEGORY": diagnosis_record.age_category or "",
                "HEIGHT": diagnosis_record.height or 0.0,
                "MENOPAUSE_YEAR": diagnosis_record.menopause_year or 0,
                "SMOKING_STATUS": diagnosis_record.smoking_status or "",
                "PHYSICAL_ACTIVITY_LEVAL": diagnosis_record.physical_activity_leval or "",
                "DIET_PLAN": diagnosis_record.diet_plan or "",
                "ALCOHOL_INTAKE": diagnosis_record.alcohol_intake or "",
            }
            
            diagnosis_record.xray_image.open()
            files = {
                'file': ('xray.jpg', diagnosis_record.xray_image.read(), 'image/jpeg')
            }
            data = {
                'structured_data': json.dumps(structured_data)
            }
            
            response = requests.post(url, files=files, data=data, timeout=10)
            diagnosis_record.xray_image.close()
            
            if response.status_code == 200:
                result = response.json()
                diagnosis_record.pred_class = result.get('prediction_class')
                diagnosis_record.confidence_score = result.get('confidence_score')
                diagnosis_record.risk_level = result.get('risk_level', '').upper()
                diagnosis_record.status = 'COMPLETED'
                diagnosis_record.error_message = result.get('explanation', '')
                
                
            else:
                diagnosis_record.status = 'FAILED'
                diagnosis_record.error_message = f"ML Service returned {response.status_code}: {response.text}"
                
        except Exception as e:
            diagnosis_record.status = 'FAILED'
            diagnosis_record.error_message = str(e)
            
        diagnosis_record.save()
        return diagnosis_record
