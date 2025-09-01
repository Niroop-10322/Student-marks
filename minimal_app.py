import streamlit as st

st.title("📊 Student Marks Analyzer")

# Sample data
students = {
    'Alice': [85, 90, 78],
    'Bob': [72, 88, 91],
    'Charlie': [95, 85, 89],
    'David': [35, 65, 70]
}

st.write("## Student Marks Analysis")

# Calculate averages and find toppers
averages = {}
failed = []
for name, marks in students.items():
    avg = sum(marks) / 3
    averages[name] = round(avg, 2)
    if min(marks) < 40:
        failed.append(name)

# Display results
st.write("### All Students:")
for name, marks in students.items():
    status = "❌ Failed" if name in failed else "✅ Passed"
    st.write(f"**{name}**: Math={marks[0]}, Science={marks[1]}, English={marks[2]}, Average={averages[name]}%, {status}")

if failed:
    st.error(f"Students who failed: {', '.join(failed)}")

# Class topper
topper = max(averages, key=averages.get)
st.success(f"🏆 Class Topper: **{topper}** with {averages[topper]}% average")

# Subject toppers
st.write("### Subject Toppers:")
math_topper = max(students, key=lambda x: students[x][0])
science_topper = max(students, key=lambda x: students[x][1])
english_topper = max(students, key=lambda x: students[x][2])

st.write(f"**Math**: {math_topper}")
st.write(f"**Science**: {science_topper}")
st.write(f"**English**: {english_topper}")

st.write("### All Averages (Sorted):")
for name, avg in sorted(averages.items(), key=lambda x: x[1], reverse=True):
    grade = "A+" if avg >= 90 else "A" if avg >= 80 else "B" if avg >= 70 else "C" if avg >= 60 else "D" if avg >= 50 else "F"
    st.write(f"**{name}**: {avg}% (Grade: {grade})")
