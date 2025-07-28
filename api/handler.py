from http.server import BaseHTTPRequestHandler
import json
import os
import google.generativeai as genai

# --- Configuration ---
# Set up your Gemini API key as an Environment Variable in your Vercel project settings.
GOOGLE_API_KEY = os.environ.get("GEMINI_API_KEY")

# --- Configure the Gemini API ---
genai.configure(api_key=GOOGLE_API_KEY)
model = genai.GenerativeModel('gemma-3-27b-it')

class handler(BaseHTTPRequestHandler):

    def do_POST(self):
        content_length = int(self.headers['Content-Length'])
        post_data = self.rfile.read(content_length)
        
        try:
            data = json.loads(post_data)
            symbol = data.get('symbol')
            charts = data.get('charts')

            if not symbol or not charts:
                self.send_response(400)
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps({"error": "Symbol and charts are required."}).encode('utf-8'))
                return

            # --- Prepare Prompt for Gemini ---
            analysis_json_structure = ', '.join([f'"{chart["timeframe"]}": {{ "summary": "...", "patterns": [], "indicators": "..." }}' for chart in charts])
            
            prompt = f"""
            You are an expert institutional-level financial analyst. Your task is to perform a deep, multi-layered analysis of the provided chart screenshots for the symbol {symbol} to formulate a high-quality swing trade setup.

            **Your Analysis Process:**
            1.  **Visual Technical Analysis (3-Level Framework):** For each chart, identify the current technical setup using the 3-level framework (Retail, Stop-Hunt, Institutional zones). Deduce indicator states like RSI and MACD from the visual price action.
            2.  **Cross-Timeframe Confluence:** Synthesize the findings from all timeframes. Where do the signals align?
            3.  **Final Verdict:** Based on the confluence, provide a "YAY" or "NAY" verdict and a concise reason.

            **Goal:** Create a complete trade plan for a swing trade designed to reach its take profit target within the 4-hour mark of the trading day.

            **Output Format:**
            Return a single, minified JSON object with NO markdown formatting. The JSON must follow this exact structure:
            {{
              "tradePlan": {{ "entry": "...", "exit": "...", "stopLoss": "..." }},
              "verdict": {{ "recommendation": "YAY/NAY", "reason": "..." }},
              "confidence": {{ "probability": "...", "assessment": "..." }},
              "analysis": {{ {analysis_json_structure} }},
              "executionStrategy": "..."
            }}
            """

            # Prepare image parts for the prompt
            prompt_parts = [prompt]
            for chart in charts:
                prompt_parts.append(f"\nChart for {chart['timeframe']}:")
                prompt_parts.append({"mime_type": "image/jpeg", "data": chart['image']})

            # Call Gemini API
            response = model.generate_content(prompt_parts)
            
            # Clean and parse the response
            raw_text = response.text
            if raw_text.strip().startswith("```json"):
                raw_text = raw_text.strip()[7:-3]
            
            json_data = json.loads(raw_text)

            # Send successful response
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps(json_data).encode('utf-8'))

        except Exception as e:
            self.send_response(500)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({"error": str(e)}).encode('utf-8'))
        
        return
