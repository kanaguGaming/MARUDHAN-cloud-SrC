async def get_kural_response(query: str):
    # KURAL & UNMAI Microservices
    # Multilingual LLM + RAG + Explainable AI (UNMAI)
    
    # Simulated Explainable AI Justification
    explanation = "The system turned on the pump because soil moisture dropped below 30%."
    
    return {
        "kural_reply_tamil": "மண் ஈரம் 30% க்கும் குறைவாக இருந்ததால் பம்ப் ஆன் செய்யப்பட்டது.",
        "kural_reply_english": explanation,
        "unmai_explainable_trace": {
            "trigger_sensor": "soil_moisture",
            "trigger_value": 28.5,
            "threshold": 30.0,
            "action_dispatched": "PUMP_ON"
        }
    }
