QA_TEMPLATE = {
    "fields" :[
        {"name": "Question"},
        {"name": "Answer"},
    ],
    "templates":[
        {
            "name": "Card 1",
            "qfmt": """
<div class="qa-card">
  <div class="qa-question">
    {{Question}}
  </div>
</div>
""",
            "afmt": """
<div class="qa-card">
  <div class="qa-question">
    {{Question}}
  </div>
  <hr id="answer">
  <div class="qa-answer">
    {{Answer}}
  </div>
</div>
""",
        }
    ],
    "css":"""
.qa-card {
  max-width: 48rem;
  margin: 0 auto;
  padding: 18px 20px;
  border-radius: 12px;
  background-color: #111318;
  color: #f4f4f7;
  font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
  box-shadow: 0 10px 30px rgba(0, 0, 0, 0.35);
}

.qa-question {
  font-size: 1.15rem;
  line-height: 1.6;
}

.qa-answer {
  margin-top: 0.7rem;
  font-size: 1.02rem;
  line-height: 1.6;
  color: #d0d0dd;
}

hr#answer {
  margin: 1.0rem 0 0.4rem;
  border: none;
  border-top: 1px solid #343640;
}

/* 수식이 섞여 있을 때 너무 크지 않게만 조정 */
mjx-container {
  font-size: 1.0em;
}
""",   
}