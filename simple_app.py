import streamlit as st

st.set_page_config(
    page_title="Student Marks Analyzer",
    page_icon="📊",
    layout="wide"
)

st.title("📊 Student Marks Analyzer")
st.markdown("---")

# Sample data
students = {
    'Alice': [85, 90, 78],
    'Bob': [72, 88, 91],
    'Charlie': [95, 85, 89],
    'David': [35, 65, 70]
}

# Analysis
failed_students = []
student_averages = {}
subject_toppers = {'Math': '', 'Science': '', 'English': ''}
subject_highest = {'Math': 0, 'Science': 0, 'English': 0}
highest_average = 0
class_topper = ''

for student_name, marks in students.items():
    math, science, english = marks
    
    # Check for failing students (marks below 40)
    if math < 40 or science < 40 or english < 40:
        failed_students.append(student_name)
    
    # Calculate average marks
    average = (math + science + english) / 3
    student_averages[student_name] = round(average, 2)
    
    # Track class topper (highest average)
    if average > highest_average:
        highest_average = average
        class_topper = student_name
    
    # Track subject-wise toppers
    if math > subject_highest['Math']:
        subject_highest['Math'] = math
        subject_toppers['Math'] = student_name
    
    if science > subject_highest['Science']:
        subject_highest['Science'] = science
        subject_toppers['Science'] = student_name
    
    if english > subject_highest['English']:
        subject_highest['English'] = english
        subject_toppers['English'] = student_name

# Display results
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric("Total Students", len(students))

with col2:
    st.metric("Failed Students", len(failed_students))

with col3:
    class_avg = sum(student_averages.values()) / len(student_averages)
    st.metric("Class Average", f"{class_avg:.2f}%")

with col4:
    st.metric("Top Average", f"{student_averages[class_topper]:.2f}%")

st.markdown("---")

# Student marks table
st.subheader("📊 Student Marks Table")

for name, marks in students.items():
    status = '❌ Failed' if name in failed_students else '✅ Passed'
    st.write(f"**{name}**: Math={marks[0]}, Science={marks[1]}, English={marks[2]}, Average={student_averages[name]}%, Status={status}")

# Failed students alert
if failed_students:
    st.error(f"⚠️ Students who failed: {', '.join(failed_students)}")

st.markdown("---")

# Analysis results
col1, col2 = st.columns(2)

with col1:
    st.subheader("🏆 Class Topper")
    st.info(f"**{class_topper}** with {student_averages[class_topper]}% average")
    
    st.subheader("🥇 Subject Toppers")
    for subject, topper in subject_toppers.items():
        st.success(f"**{subject}**: {topper}")

with col2:
    st.subheader("📊 Performance Summary")
    
    for subject in ['Math', 'Science', 'English']:
        marks = [students[name][['Math', 'Science', 'English'].index(subject)] for name in students.keys()]
        avg_mark = sum(marks) / len(marks)
        highest_mark = max(marks)
        lowest_mark = min(marks)
        st.write(f"**{subject}**: Average={avg_mark:.1f}, Highest={highest_mark}, Lowest={lowest_mark}")

# All student averages
st.subheader("📈 All Student Averages")

for name, avg in sorted(student_averages.items(), key=lambda x: x[1], reverse=True):
    if avg >= 90:
        grade = "A+"
    elif avg >= 80:
        grade = "A"
    elif avg >= 70:
        grade = "B"
    elif avg >= 60:
        grade = "C"
    elif avg >= 50:
        grade = "D"
    else:
        grade = "F"
    
    st.write(f"**{name}**: {avg}% (Grade: {grade})")

st.markdown("---")
st.success("🎉 Student Marks Analysis Complete!")
