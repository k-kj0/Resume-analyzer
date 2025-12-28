import streamlit as st
import PyPDF2
import re

st.set_page_config(page_title="AI Resume Checker", layout="wide")

st.title("📋 AI Resume Analyzer")
st.write("Check how your resume matches job requirements")

# Expanded skills with variations
SKILLS = {
    "python": ["python", "python3", "py"],
    "machine learning": ["machine learning", "ml"],
    "deep learning": ["deep learning", "dl"],
    "ai": ["ai", "artificial intelligence"],
    "tensorflow": ["tensorflow", "tf"],
    "pytorch": ["pytorch"],
    "sql": ["sql", "mysql", "postgresql", "database"],
    "aws": ["aws", "amazon web services"],
    "azure": ["azure", "microsoft azure"],
    "docker": ["docker", "container"],
    "kubernetes": ["kubernetes", "k8s"],
    "git": ["git", "version control"],
    "github": ["github", "gitlab"]
}

def read_pdf(file):
    try:
        reader = PyPDF2.PdfReader(file)
        text = ""
        for page in reader.pages:
            page_text = page.extract_text()
            if page_text:
                text += page_text + " "
        return text.lower()
    except Exception as e:
        st.error(f"Error reading PDF: {str(e)}")
        return ""

def find_skills(text, skills_dict):
    found = {}
    text_lower = text.lower()
    
    for skill_name, variations in skills_dict.items():
        for variation in variations:
            pattern = r'\b' + re.escape(variation) + r'\b'
            if re.search(pattern, text_lower):
                found[skill_name] = variation
                break
    
    return found

# Input section
col1, col2 = st.columns(2)

with col1:
    st.subheader("Upload Resume")
    uploaded_file = st.file_uploader("Choose PDF file", type="pdf", key="resume_uploader")

with col2:
    st.subheader("Job Description")
    job_text = st.text_area("Paste job description here", height=150, key="job_desc")

# Add debug mode checkbox
debug_mode = st.checkbox("🔧 Debug Mode", help="Show detailed information for troubleshooting")

# Analyze button
if st.button("🔍 Analyze Resume", type="primary") and uploaded_file and job_text:
    with st.spinner("Analyzing..."):
        # Read resume
        resume_text = read_pdf(uploaded_file)
        
        if not resume_text or len(resume_text.strip()) < 10:
            st.error("Could not extract text from PDF. The PDF might be scanned or image-based.")
        else:
            # Find skills
            found_skills = find_skills(resume_text, SKILLS)
            required_skills = find_skills(job_text, SKILLS)
            
            # Debug information
            if debug_mode:
                with st.expander("🔍 Debug Information"):
                    st.subheader("Extracted Resume Text (First 500 chars):")
                    st.text(resume_text[:500] + "..." if len(resume_text) > 500 else resume_text)
                    
                    st.subheader("Found Skills Dictionary:")
                    st.write(found_skills)
                    
                    st.subheader("Required Skills Dictionary:")
                    st.write(required_skills)
            
            # Calculate score
            found_keys = list(found_skills.keys())
            required_keys = list(required_skills.keys())
            
            if required_keys:
                # Find matching skills
                matching = [skill for skill in found_keys if skill in required_keys]
                score = (len(matching) / len(required_keys)) * 100
                
                # Show results
                st.success(f"## Match Score: {score:.1f}%")
                
                col_a, col_b = st.columns(2)
                
                with col_a:
                    st.subheader("✅ Skills in Your Resume")
                    if found_keys:
                        for skill in found_keys:
                            st.write(f"✓ **{skill}**")
                    else:
                        st.info("No skills detected in resume")
                
                with col_b:
                    st.subheader("📋 Required Skills in Job")
                    for skill in required_keys:
                        st.write(f"• **{skill}**")
                    
                    st.write("---")
                    
                    # Missing skills
                    missing = [skill for skill in required_keys if skill not in found_keys]
                    if missing:
                        st.error("### Missing Skills")
                        for skill in missing:
                            st.write(f"✗ **{skill}**")
                    else:
                        st.success("### ✅ Perfect Match!")
            
            else:
                st.warning("## ⚠️ No Skills Detected in Job Description")
                st.info("""
                **Try adding specific skills to the job description:**
                - python, machine learning, sql
                - aws, azure, docker
                - git, github, tensorflow
                """)
                
                # Still show what we found in resume
                if found_keys:
                    st.write("**Skills found in your resume:**")
                    for skill in found_keys:
                        st.write(f"✓ {skill}")

else:
    st.info("📝 Please upload a resume PDF and paste a job description")

st.write("---")
st.markdown("""
### 💡 **Tips for Best Results:**
1. **Use text-based PDFs** (not scanned/image PDFs)
2. **Be specific in job description**: Include skills like "Python", "SQL", "AWS"
3. **Spell skills correctly** in your resume
4. **Common formats work best**: Word/PDF with selectable text
""")
st.write("Built with Streamlit • Deploy on Streamlit Cloud")
