import panel as pn
from openai import OpenAI
import io
import re
import requests
from reportlab.platypus import SimpleDocTemplate, Paragraph, Image as RLImage
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import inch

pn.extension()

# Custom styles
pn.config.raw_css.append("""
.fade-in {
    animation: fadeIn 0.8s ease-in forwards;
}
@keyframes fadeIn {
    from { opacity: 0; transform: translateY(20px); }
    to { opacity: 1; transform: translateY(0); }
}
.glow-button {
    box-shadow: 0 0 8px #33ccff;
}
.glow-button:hover {
    box-shadow: 0 0 15px #00e6e6;
    transition: box-shadow 0.3s ease-in-out;
}
.gradient-text {
    background: linear-gradient(90deg, #ff0080, #7928ca);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    font-weight: bold;
}
button:hover {
    transform: scale(1.05);
    transition: transform 0.2s ease-in-out;
}
img {
    border-radius: 12px;
}
""")

client = OpenAI()

def create_app():
    # UI Elements
    subject_selector = pn.widgets.Select(name="Choose a Subject",
                                         options=["Math", "Science", "History", "Art", "Technology"])
    grade_selector = pn.widgets.Select(name="Select Grade Level",
                                       options=["Elementary", "Middle School", "High School"])
    project_type_selector = pn.widgets.Select(name="Project Type",
                                              options=["Creative", "Research", "Hands-on", "Collaborative"])

    generate_button = pn.widgets.Button(name="Generate Idea", button_type="primary", css_classes=["glow-button"])
    regenerate_button = pn.widgets.Button(name="🔁 Try Another", button_type="default")
    header = pn.pane.HTML("<h2 class='gradient-text'>🎨 Idea Generator</h2>")
    loading_indicator = pn.pane.Markdown("⏳ Generating your idea and image... Please wait...", visible=False)
    loading_spinner = pn.indicators.LoadingSpinner(value=True, width=40, visible=False)

    top_output = pn.pane.Markdown("", styles={'font-size': '16px'})
    image_pane = pn.pane.Image(width=512, height=512, visible=False)
    bottom_output = pn.pane.Markdown("", styles={'font-size': '16px'})

    idea_text = {"content": "", "image_url": None}
    typing_callback = {"cb": None}

    def simulate_typing(text, target_output):
        target_output.object = ""
        target_output.css_classes = ["fade-in"]
        i = [0]
        def update():
            if i[0] < len(text):
                target_output.object += text[i[0]]
                i[0] += 1
            else:
                if typing_callback["cb"]:
                    typing_callback["cb"].stop()
        if typing_callback["cb"]:
            typing_callback["cb"].stop()
        typing_callback["cb"] = pn.state.add_periodic_callback(update, period=20)

    def split_idea_sections(text):
        match = re.search(r"(\n\d+\.\s|\nSteps?:)", text)
        if match:
            idx = match.start()
            return text[:idx], text[idx:]
        return text, ""

    def get_pdf_bytes():
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(buffer)
        styles = getSampleStyleSheet()
        story = [Paragraph(p, styles["Normal"]) for p in idea_text["content"].split("\n\n")]
        if idea_text["image_url"]:
            try:
                img_data = requests.get(idea_text["image_url"]).content
                story.append(RLImage(io.BytesIO(img_data), width=4*inch, height=4*inch))
            except Exception as e:
                story.append(Paragraph(f"⚠️ Image error: {e}", styles["Normal"]))
        doc.build(story)
        buffer.seek(0)
        return buffer

    download_button = pn.widgets.FileDownload(
        label="📥 Download PDF", button_type="success",
        filename="idea.pdf", callback=get_pdf_bytes,
        visible=False
    )

    def generate_idea(subject, grade, ptype):
        loading_indicator.visible = True
        loading_spinner.visible = True
        image_pane.visible = False
        top_output.object = ""
        bottom_output.object = ""
        idea_text["image_url"] = None

        try:
            prompt = (
                f"Suggest a {ptype.lower()} learning project idea suitable for {grade.lower()} students "
                f"in the subject of {subject}. Include a title, description, and steps."
            )
            response = client.chat.completions.create(
                model="gpt-4",
                messages=[{"role": "user", "content": prompt}]
            )
            idea = response.choices[0].message.content
            markdown = f"### 💡 Project Idea for {subject}\n\n{idea}"
            idea_text["content"] = markdown

            top, bottom = split_idea_sections(markdown)
            simulate_typing(top, top_output)
            bottom_output.object = bottom
            download_button.visible = True

            img_response = client.images.generate(
                model="dall-e-3", prompt=prompt, size="1024x1024", n=1
            )
            image_url = img_response.data[0].url
            image_pane.object = image_url
            image_pane.visible = True
            idea_text["image_url"] = image_url

        except Exception as e:
            top_output.object = f"⚠️ Error: {e}"
            bottom_output.object = ""
            image_pane.visible = False
            download_button.visible = False
        finally:
            loading_indicator.visible = False
            loading_spinner.visible = False

    generate_button.on_click(lambda e: generate_idea(
        subject_selector.value, grade_selector.value, project_type_selector.value))
    regenerate_button.on_click(lambda e: generate_idea(
        subject_selector.value, grade_selector.value, project_type_selector.value))

    return pn.Column(
        header,
        pn.Row(subject_selector, grade_selector, project_type_selector),
        pn.Row(generate_button, regenerate_button, download_button),
        loading_indicator,
        pn.Row(pn.Spacer(width=20), loading_spinner),
        pn.Spacer(height=10),
        top_output,
        image_pane,
        bottom_output
    )

