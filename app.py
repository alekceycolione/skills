import os
from pathlib import Path

import pyperclip
import streamlit as st
from dotenv import load_dotenv

from core.ai_client import call_gemini, list_gemini_models
from core.prompt_builder import build_export_text, build_prompt
from core.skill_reader import list_skills, load_skill, save_skill_md
from core.file_parser import extract_text_from_file

load_dotenv()

# Detect local `skills/` folder dynamically within the repo
LOCAL_SKILLS_DIR = Path(__file__).resolve().parent / "skills"
DEFAULT_MAC_DIR = Path.home() / "Documents/SkillHub"

# Priority 1: env var (if explicitly set, not empty, and different from Mac default when on Cloud)
env_var = os.getenv("SKILLHUB_ROOT", "").strip()

if env_var and Path(env_var).exists() and env_var != str(DEFAULT_MAC_DIR):
    DEFAULT_SKILLHUB_ROOT = Path(env_var)
elif LOCAL_SKILLS_DIR.exists():
    # Priority 2: local `skills/` folder (ideal for Streamlit Cloud)
    DEFAULT_SKILLHUB_ROOT = LOCAL_SKILLS_DIR
else:
    # Priority 3: Fallback to local Mac folder 
    DEFAULT_SKILLHUB_ROOT = DEFAULT_MAC_DIR

SKILLHUB_ROOT = DEFAULT_SKILLHUB_ROOT
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")

# ── Page config ──────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="AI Skill Hub",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Session state defaults ───────────────────────────────────────────────────
st.session_state.setdefault("response", "")
st.session_state.setdefault("prompt", "")
st.session_state.setdefault("skill_content", "")

# ── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.title("🧠 AI Skill Hub")
    st.caption(f"`{SKILLHUB_ROOT}`")

    skills = list_skills(SKILLHUB_ROOT)

    if not skills:
        st.warning(
            f"Nenhuma Skill encontrada em `{SKILLHUB_ROOT}`.\n\n"
            "Crie uma subpasta com um arquivo `SKILL.md` para começar."
        )
        st.stop()

    selected_skill = st.selectbox("📂 Selecionar Skill", skills)

    if st.button("🔄 Atualizar", use_container_width=True):
        st.rerun()

    st.divider()

    # Per-skill config display
    skill_data = load_skill(SKILLHUB_ROOT, selected_skill)
    cfg = skill_data["config"]
    if cfg:
        st.caption(f"**Temperatura:** {cfg.get('temperature', 0.7)}")

# ── Load skill on selection change ────────────────────────────────────────────
if "last_skill" not in st.session_state or st.session_state.last_skill != selected_skill:
    st.session_state.skill_content = skill_data["instructions"]
    st.session_state.response = ""
    st.session_state.prompt = ""
    st.session_state.last_skill = selected_skill

# ── Main Layout ───────────────────────────────────────────────────────────────
st.header(f"📋 {selected_skill}", divider="gray")

col_editor, col_query = st.columns([4, 6], gap="large")

# ── Column 1: SKILL.md Editor ─────────────────────────────────────────────────
with col_editor:
    st.subheader("📝 SKILL.md")
    edited_content = st.text_area(
        label="Instruções da Skill",
        value=st.session_state.skill_content,
        height=380,
        label_visibility="collapsed",
    )

    if st.button("💾 Salvar SKILL.md", use_container_width=True):
        save_skill_md(SKILLHUB_ROOT, selected_skill, edited_content)
        st.session_state.skill_content = edited_content
        st.success("✅ Salvo com sucesso!")

    if skill_data["context"]:
        with st.expander("📄 CONTEXT.txt"):
            st.text(skill_data["context"])

# ── Column 2: Query + Response ────────────────────────────────────────────────
with col_query:
    st.subheader("💬 Query")
    
    uploaded_file = st.file_uploader(
        "📄 Anexar Arquivo (Opcional)", 
        type=["txt", "pdf", "docx"],
        help="Envie um artigo ou documento para usar como contexto nesta skill."
    )
    
    extracted_text = ""
    if uploaded_file is not None:
        with st.spinner("Extraindo texto..."):
            extracted_text = extract_text_from_file(uploaded_file)
            if extracted_text and not extracted_text.startswith("[Erro"):
                st.success(f"Texto extraído: {len(extracted_text)} caracteres")
            else:
                st.error(extracted_text or "Não foi possível extrair o texto.")

    query = st.text_area(
        label="Sua pergunta ou tarefa",
        placeholder="Descreva sua pergunta ou tarefa para a IA...",
        height=140,
        label_visibility="collapsed",
    )

    api_key_input = st.text_input(
        "🔑 Gemini API Key",
        value=GEMINI_API_KEY,
        type="password",
        help="Carregada automaticamente do .env. Sobrescreva aqui se necessário.",
    )

    @st.cache_data(ttl=300)
    def cached_models(key: str) -> list[str]:
        return list_gemini_models(key)
    
    available_models = cached_models(api_key_input)
    cfg_model = skill_data["config"].get("model", available_models[0])
    # Fallback caso o modelo do config não esteja na lista
    default_index = available_models.index(cfg_model) if cfg_model in available_models else 0
    
    selected_model_ui = st.selectbox("🤖 Modelo", available_models, index=default_index)
    skill_data["config"]["model"] = selected_model_ui

    send_col, _ = st.columns([1, 3])
    with send_col:
        send_clicked = st.button("🚀 Enviar", type="primary", use_container_width=True)

    if send_clicked:
        has_query = bool(query.strip())
        has_file = bool(extracted_text and not extracted_text.startswith("[Erro"))
        
        if not has_query and not has_file:
            st.warning("Digite uma query ou envie um arquivo antes de enviar.")
        else:
            active_content = edited_content.strip() or st.session_state.skill_content
            
            # Combine skill context with extracted text if available
            combined_context = skill_data["context"] or ""
            if extracted_text and not extracted_text.startswith("[Erro"):
                if combined_context:
                    combined_context += "\n\n---\n\n"
                combined_context += "### TEXTO ANEXADO PELO USUÁRIO:\n" + extracted_text
                
            built_prompt = build_prompt(
                instructions=active_content,
                context=combined_context,
                query=query,
            )
            st.session_state.prompt = built_prompt

            with st.spinner("Processando com Gemini..."):
                try:
                    st.session_state.response = call_gemini(
                        prompt=built_prompt,
                        api_key=api_key_input,
                        config=skill_data["config"],
                    )
                except Exception as e:
                    st.session_state.response = f"❌ Erro: {e}"

    if st.session_state.prompt:
        with st.expander("🔍 Ver Prompt Completo"):
            st.code(st.session_state.prompt, language="markdown")

    if st.session_state.response:
        st.subheader("🤖 Resposta")
        st.markdown(st.session_state.response)

# ── Footer: Clipboard Export ──────────────────────────────────────────────────
if st.session_state.response:
    st.divider()
    if st.button("📋 Copiar para Clipboard", use_container_width=True):
        export_text = build_export_text(
            prompt=st.session_state.prompt,
            response=st.session_state.response,
        )
        try:
            pyperclip.copy(export_text)
            st.success("✅ Copiado! Cole no Perplexity, Claude ou qualquer outra IA.")
        except pyperclip.PyperclipException:
            st.text_area("Copie manualmente:", value=export_text, height=200)
