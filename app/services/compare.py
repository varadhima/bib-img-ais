import openai
from app.config import OPENAI_API_KEY

openai.api_key = OPENAI_API_KEY

def compare_data(extracted_text: str, actual_data: dict) -> dict:
    comparison = {"matches": [], "discrepancies": []}

    for key, actual_value in actual_data.items():
        found = actual_value.lower() in extracted_text.lower()
        if found:
            comparison["matches"].append({"field": key, "value": actual_value})
        else:
            comparison["discrepancies"].append({"field": key, "value": actual_value})

    if OPENAI_API_KEY:
        prompt = f"""
        Extracted text:
        {extracted_text}

        Actual data:
        {actual_data}

        Identify discrepancies and explain if the extracted text accurately reflects the actual data.
        """
        try:
            response = openai.ChatCompletion.create(
                model="gpt-4",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=300
            )
            analysis = response.choices[0].message.content.strip()
            comparison["openai_analysis"] = analysis
        except Exception as e:
            comparison["openai_error"] = str(e)

    return comparison
