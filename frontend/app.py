"""
Streamlit Frontend for IR Sentiment Analyzer with Ollama
Provides an intuitive UI for document analysis with local LLM models
"""

import streamlit as st
import requests
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime
import os

# Configuration
API_BASE_URL = os.getenv("API_BASE_URL", "http://localhost:8000")

# Page configuration
st.set_page_config(
    page_title="IR Sentiment Analyzer (Ollama)",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: 700;
        color: #1f77b4;
        margin-bottom: 0.5rem;
    }
    .metric-card {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #1f77b4;
    }
    .score-excellent {
        color: #28a745;
        font-weight: 600;
    }
    .score-good {
        color: #17a2b8;
        font-weight: 600;
    }
    .score-fair {
        color: #ffc107;
        font-weight: 600;
    }
    .score-poor {
        color: #dc3545;
        font-weight: 600;
    }
    .ollama-status {
        padding: 0.5rem 1rem;
        border-radius: 0.25rem;
        margin-bottom: 1rem;
    }
    .status-ok {
        background-color: #d4edda;
        color: #155724;
        border: 1px solid #c3e6cb;
    }
    .status-error {
        background-color: #f8d7da;
        color: #721c24;
        border: 1px solid #f5c6cb;
    }
</style>
""", unsafe_allow_html=True)


def get_score_class(score):
    """Get CSS class based on score"""
    if score >= 80:
        return "score-excellent"
    elif score >= 65:
        return "score-good"
    elif score >= 50:
        return "score-fair"
    else:
        return "score-poor"


def get_score_label(score):
    """Get label based on score"""
    if score >= 80:
        return "Excellent"
    elif score >= 65:
        return "Good"
    elif score >= 50:
        return "Fair"
    else:
        return "Needs Improvement"


def check_ollama_status():
    """Check Ollama status and display in sidebar"""
    try:
        response = requests.get(f"{API_BASE_URL}/api/ollama/status", timeout=2)
        if response.status_code == 200:
            status = response.json()
            return status
        return {"available": False, "error": "API not responding"}
    except:
        return {"available": False, "error": "Cannot connect to backend"}


# Sidebar navigation
st.sidebar.title("📊 IR Sentiment Analyzer")
st.sidebar.caption("Powered by Ollama")

# Check Ollama status
ollama_status = check_ollama_status()
if ollama_status.get("available"):
    st.sidebar.markdown(
        f'<div class="ollama-status status-ok">✓ Ollama Running<br/>{ollama_status.get("model_count", 0)} models available</div>',
        unsafe_allow_html=True
    )
else:
    st.sidebar.markdown(
        f'<div class="ollama-status status-error">⚠ Ollama Not Available<br/>{ollama_status.get("error", "Unknown error")}</div>',
        unsafe_allow_html=True
    )
    st.sidebar.info("Please install and start Ollama: https://ollama.ai")

page = st.sidebar.radio(
    "Navigation",
    ["Dashboard", "Upload Document", "Document Analysis", "Comparisons", "Metrics & Trends", "Model Management"]
)


# Dashboard Page
if page == "Dashboard":
    st.markdown('<div class="main-header">Dashboard</div>', unsafe_allow_html=True)
    st.markdown("Manage and analyze your investor relations documents")
    
    # Fetch documents
    try:
        response = requests.get(f"{API_BASE_URL}/api/documents")
        documents = response.json() if response.status_code == 200 else []
    except:
        st.error("Unable to connect to backend API. Please ensure the server is running.")
        documents = []
    
    # Statistics
    total_docs = len(documents)
    completed_docs = len([d for d in documents if d["status"] == "completed"])
    processing_docs = len([d for d in documents if d["status"] == "processing"])
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Total Documents", total_docs)
    with col2:
        st.metric("Completed Analyses", completed_docs)
    with col3:
        st.metric("Processing", processing_docs)
    
    st.markdown("---")
    
    # Recent documents
    st.subheader("Recent Documents")
    
    if documents:
        for doc in documents[:10]:
            with st.container():
                col1, col2, col3, col4 = st.columns([3, 1, 1, 1])
                
                with col1:
                    st.markdown(f"**{doc['title']}**")
                    st.caption(doc['document_type'].replace('_', ' ').title())
                
                with col2:
                    status_color = {
                        "completed": "🟢",
                        "processing": "🟡",
                        "failed": "🔴",
                        "uploading": "⚪"
                    }
                    st.markdown(f"{status_color.get(doc['status'], '⚪')} {doc['status'].title()}")
                
                with col3:
                    created = datetime.fromisoformat(doc['created_at'].replace('Z', '+00:00'))
                    st.caption(created.strftime("%Y-%m-%d"))
                
                with col4:
                    if doc['status'] == 'completed':
                        if st.button("View Analysis", key=f"view_{doc['id']}"):
                            st.session_state['selected_document_id'] = doc['id']
                            st.rerun()
                
                st.markdown("---")
    else:
        st.info("No documents yet. Upload your first document to get started!")


# Upload Document Page
elif page == "Upload Document":
    st.markdown('<div class="main-header">Upload Document</div>', unsafe_allow_html=True)
    st.markdown("Upload a press release, earnings call transcript, or corporate document for analysis")
    
    # Check Ollama status first
    if not ollama_status.get("available"):
        st.error("⚠️ Ollama is not running. Please start Ollama before uploading documents.")
        st.info("Install Ollama from https://ollama.ai and run: `ollama serve`")
        st.stop()
    
    # Get available models
    try:
        response = requests.get(f"{API_BASE_URL}/api/ollama/models")
        if response.status_code == 200:
            models_data = response.json()
            installed_models = models_data.get("installed", [])
            recommended_models = models_data.get("recommended", [])
        else:
            installed_models = []
            recommended_models = []
    except:
        st.error("Unable to fetch models from Ollama")
        installed_models = []
        recommended_models = []
    
    if not installed_models:
        st.warning("⚠️ No models installed. Please install a model first.")
        st.info("Run: `ollama pull llama3.2` or `ollama pull mistral`")
        st.stop()
    
    with st.form("upload_form"):
        title = st.text_input("Document Title", placeholder="Q4 2024 Earnings Call")
        
        document_type = st.selectbox(
            "Document Type",
            ["press_release", "earnings_call", "corporate_release", "other"],
            format_func=lambda x: x.replace('_', ' ').title()
        )
        
        # Model selection
        st.subheader("Select Analysis Model")
        
        # Show recommended models if available
        if recommended_models:
            st.caption("Recommended models for IR analysis:")
            for rec in recommended_models:
                if rec["name"] in installed_models and rec.get("recommended"):
                    st.markdown(f"✓ **{rec['name']}** ({rec['size']}) - {rec['description']}")
        
        model = st.selectbox(
            "Model",
            installed_models,
            help="Select the Ollama model to use for analysis. Larger models provide better quality but take longer."
        )
        
        # Model info
        if model:
            with st.expander("ℹ️ About this model"):
                st.write(f"**Selected model:** {model}")
                st.write("Analysis typically takes 1-3 minutes depending on document length and model size.")
                if st.button("Test Model"):
                    with st.spinner("Testing model..."):
                        try:
                            test_response = requests.post(
                                f"{API_BASE_URL}/api/ollama/test-model",
                                json={"model": model}
                            )
                            if test_response.status_code == 200:
                                st.success(f"✓ Model '{model}' is working correctly!")
                            else:
                                st.error(f"Model test failed: {test_response.json().get('detail', 'Unknown error')}")
                        except Exception as e:
                            st.error(f"Error testing model: {str(e)}")
        
        uploaded_file = st.file_uploader(
            "Choose a file",
            type=['pdf', 'txt', 'doc', 'docx'],
            help="Supported formats: PDF, TXT, DOC, DOCX (max 10MB)"
        )
        
        submit = st.form_submit_button("Upload and Analyze")
        
        if submit:
            if not title:
                st.error("Please enter a document title")
            elif not uploaded_file:
                st.error("Please select a file to upload")
            elif not model:
                st.error("Please select a model")
            else:
                with st.spinner(f"Uploading and analyzing document with {model}... This may take 1-3 minutes."):
                    try:
                        files = {"file": uploaded_file}
                        data = {
                            "title": title,
                            "document_type": document_type,
                            "model": model
                        }
                        
                        response = requests.post(
                            f"{API_BASE_URL}/api/documents",
                            files=files,
                            data=data,
                            timeout=300  # 5 minute timeout for local models
                        )
                        
                        if response.status_code == 200:
                            st.success("✅ Document uploaded and analyzed successfully!")
                            st.balloons()
                            result = response.json()
                            st.info(f"Document ID: {result['id']}")
                            st.info(f"Analyzed with model: {model}")
                        else:
                            error_detail = response.json().get('detail', 'Unknown error')
                            st.error(f"Upload failed: {error_detail}")
                    
                    except requests.exceptions.Timeout:
                        st.error("Analysis timed out. The model may be too slow or the document too large. Try a smaller model or shorter document.")
                    except Exception as e:
                        st.error(f"Error: {str(e)}")


# Document Analysis Page  
elif page == "Document Analysis":
    st.markdown('<div class="main-header">Document Analysis</div>', unsafe_allow_html=True)
    
    # Get document ID from session state or selection
    if 'selected_document_id' not in st.session_state:
        # Fetch documents for selection
        try:
            response = requests.get(f"{API_BASE_URL}/api/documents")
            documents = response.json() if response.status_code == 200 else []
            completed_docs = [d for d in documents if d["status"] == "completed"]
            
            if completed_docs:
                selected = st.selectbox(
                    "Select a document",
                    completed_docs,
                    format_func=lambda x: f"{x['title']} ({x['document_type'].replace('_', ' ').title()})"
                )
                document_id = selected['id']
            else:
                st.info("No completed analyses available. Upload a document first.")
                st.stop()
        except:
            st.error("Unable to connect to backend API")
            st.stop()
    else:
        document_id = st.session_state['selected_document_id']
    
    # Fetch analysis
    try:
        response = requests.get(f"{API_BASE_URL}/api/documents/{document_id}/analysis")
        if response.status_code == 200:
            data = response.json()
            analysis = data['analysis']
            sections = data['sections']
        else:
            st.error("Analysis not found")
            st.stop()
    except:
        st.error("Unable to fetch analysis")
        st.stop()
    
    # Display analysis
    st.subheader("Overall Analysis")
    
    # Metrics
    col1, col2, col3, col4, col5 = st.columns(5)
    
    metrics = [
        ("Sentiment", analysis['sentiment_score']),
        ("Confidence", analysis['confidence_score']),
        ("Clarity", analysis['clarity_score']),
        ("Readability", analysis['readability_score']),
        ("Specificity", analysis['specificity_score'])
    ]
    
    for col, (label, score) in zip([col1, col2, col3, col4, col5], metrics):
        with col:
            st.metric(label, f"{score}/100")
            st.caption(get_score_label(score))
    
    st.markdown("---")
    
    # Tabs for different views
    tab1, tab2, tab3, tab4 = st.tabs(["Overview", "Sections", "Emotional Tone", "Linguistic Metrics"])
    
    with tab1:
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("Overall Sentiment")
            st.markdown(f"**{analysis['overall_sentiment'].title()}**")
            
            st.subheader("Key Themes")
            for theme in analysis['key_themes']:
                st.markdown(f"• {theme}")
        
        with col2:
            # Radar chart of scores
            fig = go.Figure()
            
            fig.add_trace(go.Scatterpolar(
                r=[analysis['sentiment_score'], analysis['confidence_score'],
                   analysis['clarity_score'], analysis['readability_score'],
                   analysis['specificity_score']],
                theta=['Sentiment', 'Confidence', 'Clarity', 'Readability', 'Specificity'],
                fill='toself',
                name='Scores'
            ))
            
            fig.update_layout(
                polar=dict(radialaxis=dict(visible=True, range=[0, 100])),
                showlegend=False,
                height=400
            )
            
            st.plotly_chart(fig, use_container_width=True)
    
    with tab2:
        st.subheader("Section-by-Section Analysis")
        
        for idx, section in enumerate(sections):
            with st.expander(f"📄 {section['section_title']}", expanded=(idx == 0)):
                if section['speaker']:
                    st.caption(f"Speaker: {section['speaker']}")
                
                # Section scores
                col1, col2, col3, col4, col5 = st.columns(5)
                col1.metric("Sentiment", section['sentiment_score'])
                col2.metric("Confidence", section['confidence_score'])
                col3.metric("Clarity", section['clarity_score'])
                col4.metric("Readability", section['readability_score'])
                col5.metric("Specificity", section['specificity_score'])
                
                st.markdown("**Original Text (excerpt):**")
                st.text_area("", section['original_text'][:500], height=100, key=f"orig_{idx}", disabled=True)
                
                if section['issues']:
                    st.markdown("**Identified Issues:**")
                    for issue in section['issues']:
                        st.markdown(f"⚠️ {issue}")
                
                st.markdown("**Suggested Revision:**")
                st.info(section['suggested_revision'])
                
                st.markdown("**Rationale:**")
                st.caption(section['revision_rationale'])
    
    with tab3:
        st.subheader("Emotional Tone Distribution")
        
        tone_data = analysis['emotional_tone']
        
        fig = go.Figure(data=[
            go.Bar(
                x=list(tone_data.keys()),
                y=list(tone_data.values()),
                marker_color=['#28a745', '#dc3545', '#6c757d', '#17a2b8', '#ffc107']
            )
        ])
        
        fig.update_layout(
            xaxis_title="Tone",
            yaxis_title="Percentage",
            yaxis=dict(range=[0, 100]),
            height=400
        )
        
        st.plotly_chart(fig, use_container_width=True)
    
    with tab4:
        st.subheader("Linguistic Metrics")
        
        metrics = analysis['linguistic_metrics']
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.metric("Average Sentence Length", f"{metrics['avgSentenceLength']:.1f} words")
            st.metric("Complex Word Ratio", f"{metrics['complexWordRatio']:.1%}")
            st.metric("Passive Voice Ratio", f"{metrics['passiveVoiceRatio']:.1%}")
        
        with col2:
            st.metric("Jargon Density", f"{metrics['jargonDensity']:.1%}")
            st.metric("Hedging Language", f"{metrics['hedgingLanguage']:.1%}")


# Comparisons Page (same as before)
elif page == "Comparisons":
    st.markdown('<div class="main-header">Document Comparisons</div>', unsafe_allow_html=True)
    
    # Fetch comparisons
    try:
        response = requests.get(f"{API_BASE_URL}/api/comparisons")
        comparisons = response.json() if response.status_code == 200 else []
    except:
        st.error("Unable to connect to backend API")
        comparisons = []
    
    # Create new comparison
    with st.expander("➕ Create New Comparison"):
        with st.form("comparison_form"):
            title = st.text_input("Comparison Title", placeholder="Q3 vs Q4 Earnings")
            description = st.text_area("Description (optional)", placeholder="Comparing quarterly performance...")
            
            # Get completed documents
            try:
                response = requests.get(f"{API_BASE_URL}/api/documents")
                documents = response.json() if response.status_code == 200 else []
                completed_docs = [d for d in documents if d["status"] == "completed"]
                
                selected_docs = st.multiselect(
                    "Select documents to compare (minimum 2)",
                    completed_docs,
                    format_func=lambda x: f"{x['title']} ({x['document_type'].replace('_', ' ').title()})"
                )
            except:
                st.error("Unable to fetch documents")
                selected_docs = []
            
            submit = st.form_submit_button("Create Comparison")
            
            if submit:
                if len(selected_docs) < 2:
                    st.error("Please select at least 2 documents")
                elif not title:
                    st.error("Please enter a title")
                else:
                    try:
                        payload = {
                            "title": title,
                            "description": description if description else None,
                            "document_ids": [d['id'] for d in selected_docs]
                        }
                        
                        response = requests.post(f"{API_BASE_URL}/api/comparisons", json=payload)
                        
                        if response.status_code == 200:
                            st.success("✅ Comparison created successfully!")
                            st.rerun()
                        else:
                            st.error(f"Failed to create comparison: {response.json().get('detail', 'Unknown error')}")
                    except Exception as e:
                        st.error(f"Error: {str(e)}")
    
    st.markdown("---")
    
    # Display comparisons
    if comparisons:
        for comp in comparisons:
            with st.expander(f"📊 {comp['title']}", expanded=False):
                if comp['description']:
                    st.caption(comp['description'])
                
                st.caption(f"Created: {datetime.fromisoformat(comp['created_at'].replace('Z', '+00:00')).strftime('%Y-%m-%d %H:%M')}")
                st.caption(f"Documents: {len(comp['document_ids'])}")
                
                if st.button("View Comparison", key=f"view_comp_{comp['id']}"):
                    # Fetch detailed comparison
                    try:
                        response = requests.get(f"{API_BASE_URL}/api/comparisons/{comp['id']}")
                        if response.status_code == 200:
                            detail = response.json()
                            
                            # Create comparison table
                            metrics = ['sentiment_score', 'confidence_score', 'clarity_score',
                                     'readability_score', 'specificity_score']
                            
                            data = []
                            for doc_data in detail['documents']:
                                doc = doc_data['document']
                                analysis = doc_data['analysis']
                                
                                if analysis:
                                    row = {'Document': doc['title']}
                                    for metric in metrics:
                                        row[metric.replace('_', ' ').title()] = analysis[metric]
                                    data.append(row)
                            
                            if data:
                                df = pd.DataFrame(data)
                                st.dataframe(df, use_container_width=True)
                                
                                # Comparison chart
                                fig = go.Figure()
                                
                                for idx, row in enumerate(data):
                                    fig.add_trace(go.Scatterpolar(
                                        r=[row[m.replace('_', ' ').title()] for m in metrics],
                                        theta=[m.replace('_', ' ').title() for m in metrics],
                                        fill='toself',
                                        name=row['Document']
                                    ))
                                
                                fig.update_layout(
                                    polar=dict(radialaxis=dict(visible=True, range=[0, 100])),
                                    height=500
                                )
                                
                                st.plotly_chart(fig, use_container_width=True)
                    except Exception as e:
                        st.error(f"Error loading comparison: {str(e)}")
    else:
        st.info("No comparisons yet. Create your first comparison above!")


# Metrics & Trends Page (same as before)
elif page == "Metrics & Trends":
    st.markdown('<div class="main-header">Metrics & Trends</div>', unsafe_allow_html=True)
    
    # Fetch metrics
    try:
        response = requests.get(f"{API_BASE_URL}/api/metrics/history?limit=100")
        metrics = response.json() if response.status_code == 200 else []
    except:
        st.error("Unable to connect to backend API")
        metrics = []
    
    if not metrics:
        st.info("No metrics data available yet. Upload and analyze documents to see trends.")
    else:
        # Convert to DataFrame
        df = pd.DataFrame(metrics)
        df['recorded_at'] = pd.to_datetime(df['recorded_at'])
        
        # Metrics over time
        st.subheader("Metrics Over Time")
        
        metric_to_plot = st.selectbox(
            "Select metric",
            ['sentiment_score', 'confidence_score', 'clarity_score', 'readability_score', 'specificity_score'],
            format_func=lambda x: x.replace('_', ' ').title()
        )
        
        fig = px.line(
            df,
            x='recorded_at',
            y=metric_to_plot,
            title=f"{metric_to_plot.replace('_', ' ').title()} Over Time",
            markers=True
        )
        
        fig.update_layout(
            xaxis_title="Date",
            yaxis_title="Score",
            yaxis=dict(range=[0, 100]),
            height=400
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
        st.markdown("---")
        
        # Average scores
        st.subheader("Average Scores")
        
        col1, col2, col3, col4, col5 = st.columns(5)
        
        avg_metrics = [
            ("Sentiment", df['sentiment_score'].mean()),
            ("Confidence", df['confidence_score'].mean()),
            ("Clarity", df['clarity_score'].mean()),
            ("Readability", df['readability_score'].mean()),
            ("Specificity", df['specificity_score'].mean())
        ]
        
        for col, (label, score) in zip([col1, col2, col3, col4, col5], avg_metrics):
            with col:
                st.metric(label, f"{score:.1f}")
        
        st.markdown("---")
        
        # By document type
        st.subheader("Metrics by Document Type")
        
        doc_type_avg = df.groupby('document_type')[['sentiment_score', 'confidence_score',
                                                      'clarity_score', 'readability_score',
                                                      'specificity_score']].mean()
        
        st.dataframe(doc_type_avg, use_container_width=True)


# Model Management Page
elif page == "Model Management":
    st.markdown('<div class="main-header">Model Management</div>', unsafe_allow_html=True)
    st.markdown("Manage your Ollama models for document analysis")
    
    # Check Ollama status
    status = check_ollama_status()
    
    if not status.get("available"):
        st.error(f"⚠️ Ollama is not available: {status.get('error', 'Unknown error')}")
        st.info("Please install Ollama from https://ollama.ai and run: `ollama serve`")
        st.stop()
    
    st.success(f"✓ Ollama is running with {status.get('model_count', 0)} models installed")
    
    # Get models
    try:
        response = requests.get(f"{API_BASE_URL}/api/ollama/models")
        if response.status_code == 200:
            models_data = response.json()
            installed_models = models_data.get("installed", [])
            recommended_models = models_data.get("recommended", [])
        else:
            installed_models = []
            recommended_models = []
    except:
        st.error("Unable to fetch models")
        installed_models = []
        recommended_models = []
    
    # Installed models
    st.subheader("Installed Models")
    
    if installed_models:
        for model in installed_models:
            col1, col2 = st.columns([3, 1])
            with col1:
                st.markdown(f"**{model}**")
            with col2:
                if st.button("Test", key=f"test_{model}"):
                    with st.spinner(f"Testing {model}..."):
                        try:
                            test_response = requests.post(
                                f"{API_BASE_URL}/api/ollama/test-model",
                                json={"model": model},
                                timeout=30
                            )
                            if test_response.status_code == 200:
                                st.success(f"✓ {model} is working!")
                            else:
                                st.error(f"Test failed: {test_response.json().get('detail', 'Unknown error')}")
                        except Exception as e:
                            st.error(f"Error: {str(e)}")
    else:
        st.info("No models installed yet.")
    
    st.markdown("---")
    
    # Recommended models
    st.subheader("Recommended Models for IR Analysis")
    
    for rec in recommended_models:
        with st.expander(f"{'⭐ ' if rec.get('recommended') else ''}{rec['name']} ({rec['size']})"):
            st.write(rec['description'])
            
            is_installed = rec['name'] in installed_models
            
            if is_installed:
                st.success("✓ Already installed")
            else:
                st.info(f"To install: `ollama pull {rec['name']}`")
    
    st.markdown("---")
    
    # Installation instructions
    st.subheader("How to Install Models")
    
    st.markdown("""
    1. Open a terminal/command prompt
    2. Run: `ollama pull <model-name>`
    3. Wait for download to complete
    4. Refresh this page
    
    **Examples:**
    ```bash
    ollama pull llama3.2
    ollama pull mistral
    ollama pull llama3.1
    ```
    
    **Note:** Larger models provide better analysis quality but require more RAM and take longer to run.
    """)


# Footer
st.sidebar.markdown("---")
st.sidebar.caption("IR Sentiment Analyzer v2.0 (Ollama)")
st.sidebar.caption("© 2024 All rights reserved")

