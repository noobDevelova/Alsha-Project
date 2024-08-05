import streamlit as st
import json
import os
import numpy as np

# Fungsi untuk memuat dan menyimpan data
def load_data(file_name):
    if os.path.exists(file_name):
        with open(file_name, 'r') as f:
            return json.load(f)
    return []

def save_data(data, file_name):
    with open(file_name, 'w') as f:
        json.dump(data, f, indent=4)

# Fungsi kesesuaian untuk karyawan dan proyek
def fungsiObjektif(karyawan, proyek):
    score = 0
    sertifikasi_sesuai = set(karyawan.get("certifications", [])) \
        .intersection(set(proyek.get("required_certifications", [])))
    score += len(sertifikasi_sesuai) * 10
    keterampilan_sesuai = set(karyawan.get("skills", [])) \
        .intersection(set(proyek.get("required_skills", [])))
    score += len(keterampilan_sesuai) * 10
    return score

# Inisialisasi populasi dengan karyawan acak
def inisialisasiPopulasi(ukuranPopulasi, worker_vectors):
    return [np.random.permutation(len(worker_vectors)).tolist() for _ in range(ukuranPopulasi)]

# Fungsi crossover untuk menghasilkan individu baru
def crossover(parent1, parent2):
    point = np.random.randint(1, len(parent1))
    child1 = parent1[:point] + [x for x in parent2 if x not in parent1[:point]]
    child2 = parent2[:point] + [x for x in parent1 if x not in parent2[:point]]
    return child1, child2

# Mutasi pada individu
def mutasi(individu):
    if np.random.rand() < 0.1:  # Probabilitas mutasi
        idx1, idx2 = np.random.choice(len(individu), 2, replace=False)
        individu[idx1], individu[idx2] = individu[idx2], individu[idx1]

# Fungsi untuk memilih orang tua berdasarkan fitness
def seleksi(populasi, fitness):
    tournament_size = 2
    parents = []
    for _ in range(len(populasi) // 2):
        competitors = np.random.choice(len(populasi), tournament_size, replace=False)
        best = competitors[np.argmax(fitness[competitors])]
        parents.append(best)
    return parents

# Fungsi elitisme untuk menjaga individu terbaik
def elitism(populasi, anak, fitness, fitness_anak):
    combined = np.vstack((populasi, anak))
    combined_fitness = np.concatenate((fitness, fitness_anak))
    best_indices = np.argsort(combined_fitness)[-len(populasi):]
    return combined[best_indices].tolist(), combined_fitness[best_indices].tolist()

# Fungsi algoritma genetika
def algoritmaGenetika(worker_vectors, project, ukuranPopulasi, jumlahGenerasi):
    panjangChromosome = len(worker_vectors)
    populasi = inisialisasiPopulasi(ukuranPopulasi, worker_vectors)

    for generasi in range(jumlahGenerasi):
        fitness_populasi = np.array([
            fungsiObjektif(
                worker_vectors[individu[0]], 
                project
            ) for individu in populasi
        ])

        anak = []
        for _ in range(ukuranPopulasi // 2):
            parent_indices = seleksi(populasi, fitness_populasi)
            parent1, parent2 = populasi[parent_indices[0]], populasi[parent_indices[1]]
            child1, child2 = crossover(parent1, parent2)
            mutasi(child1)
            mutasi(child2)
            anak.append(child1)
            anak.append(child2)

        fitness_anak = np.array([
            fungsiObjektif(
                worker_vectors[individu[0]], 
                project
            ) for individu in anak
        ])

        populasi, fitness_populasi = elitism(populasi, anak, fitness_populasi, fitness_anak)

    return populasi, fitness_populasi

# Fungsi klasifikasi proyek
def klasifikasi_proyek(jumlah_certifications, jumlah_skills):
    if jumlah_certifications <= 1 and jumlah_skills <= 1:
        return "Light"
    elif (jumlah_certifications <= 2 and jumlah_skills <= 2):
        return "Medium"
    else:
        return "Advanced"

def search_placement():
    st.title('Search Placement')

    project_name = st.text_input('Project Name')
    required_certifications = st.multiselect('Certifications', 
                                             ['sertifikasi - IT', 'sertifikasi - K3', 'sertifikasi - Manajemen', 
                                              'sertifikasi - Kompetensi', 'sertifikasi - MR'])
    required_skills = st.multiselect('Skills', 
                                     ['Engineer', 'Project Coordinator', 'Project Manager', 'Support Engineer', 'SE Coordinator'])

    if st.button('Search'):
        project = {
            "required_certifications": required_certifications,
            "required_skills": required_skills,
            "project_name": project_name
        }

        # Simpan data proyek ke dalam file project_data.json
        project_data = load_data('./project_data.json')
        project_data.append(project)
        save_data(project_data, './project_data.json')
        
        # Klasifikasikan proyek
        jumlah_certifications = len(required_certifications)
        jumlah_skills = len(required_skills)
        kategori_proyek = klasifikasi_proyek(jumlah_certifications, jumlah_skills)
        st.write(f'Project Category: {kategori_proyek}')

        ukuranPopulasi = 10
        jumlahGenerasi = 20
        
        populasi_terbaik, fitness_terbaik = algoritmaGenetika(worker_vectors, project, ukuranPopulasi, jumlahGenerasi)

        # Ambil beberapa individu terbaik
        num_top_individuals = 3  # Jumlah karyawan terbaik yang ingin ditampilkan
        best_indices = np.argsort(fitness_terbaik)[-num_top_individuals:]  # Ambil indeks terbaik dari fitness
        
        # Ambil nama karyawan dari indeks
        best_workers = set()
        for i in best_indices:
            if i < len(populasi_terbaik):
                best_worker_indices = populasi_terbaik[i]  # Ambil karyawan berdasarkan indeks populasi
                for worker_index in best_worker_indices:
                    worker = worker_vectors[worker_index]
                    if (set(worker["certifications"]).intersection(required_certifications) and
                        set(worker["skills"]).intersection(required_skills)):
                        best_workers.add((worker['id'], worker['name']))

        # Tampilkan karyawan terbaik yang sesuai dengan proyek
        st.write(f'The employees best suited for the project "{project_name}" are:')
        for worker_id, worker_name in best_workers:
            st.write(f'ID: {worker_id}, Nama: {worker_name}')


def Home():
    st.title('Welcome to AlssaProjectSync Employee Placement Optimization')
    st.subheader("How to Use This Application")
    st.write("""
    1. *Home*: View insights and results of the optimization process.
    2. *Search Placement*: Find the best fit for your project based on input data.
    3. *Manage Data*: Create, read, update, delete about employees and certifications
    """)

# Tambahan pada fungsi manage_data
def manage_data():
    st.title('Manage Data')

    data_type = st.sidebar.selectbox("Select Data Type", ["Employees", "Certifications", "Skills", "Projects"])

    if data_type == "Employees":
        st.subheader("Employees")
        if st.button('Refresh Data'):
            st.rerun()
        employees = load_data('./employee_data.json')
        for i, employee in enumerate(employees):
            with st.expander(f"ID: {employee['id']}, Name: {employee['name']}"):
                new_name = st.text_input(f"Edit Name for {employee['name']}", value=employee['name'], key=f"edit_name_{i}")
                
                # Validasi agar default value juga ada dalam options
                valid_certifications = [c for c in certifications_list if c in employee['certifications']]
                new_certifications = st.multiselect(
                    f"Edit Certifications {i}", certifications_list, default=valid_certifications, key=f"edit_cert_{i}"
                )
                
                valid_skills = [s for s in skills_list if s in employee['skills']]
                new_skills = st.multiselect(
                    f"Edit Skills {i}", skills_list, default=valid_skills, key=f"edit_skill_{i}"
                )
                
                if st.button(f"Save Changes {employee['id']}", key=f"save_changes_{i}"):
                    employee['name'] = new_name
                    employee['certifications'] = new_certifications
                    employee['skills'] = new_skills
                    save_data(employees, './employee_data.json')
                    st.success(f'Employee {employee["name"]} has been updated!')
                    st.rerun()
                    
                if st.button(f"Delete Employee {employee['id']}", key=f"delete_employee_{i}"):
                    employees.remove(employee)
                    save_data(employees, './employee_data.json')
                    st.success(f'Employee {employee["name"]} has been deleted!')
                    st.rerun()

        st.title('Input Data Employee')

        name = st.text_input('Employee Name', key='input_name')
        certifications = st.multiselect('Certifications', certifications_list, key='input_cert')
        skills = st.multiselect('Skills', skills_list, key='input_skill')
        
        if st.button('Submit', key='submit_employee'):
            new_id = "W" + str(len(employees) + 1).zfill(3)
            new_employee = {
                "id": new_id,
                "certifications": certifications,
                "skills": skills,
                "name": name
            }
            employees.append(new_employee)
            save_data(employees, './employee_data.json')  # Simpan data setelah menambahkan karyawan baru
            st.success(f'Employee {name} has been successfully added!')
            st.rerun()

    elif data_type == "Certifications":
        st.subheader("Certifications")
        if st.button('Refresh Data'):
            st.rerun()
        certifications = load_data('./certifications.json')
        for i, certification in enumerate(certifications):
            with st.expander(certification):
                new_certification = st.text_input("Edit Certification", value=certification, key=f"edit_certification_{i}")
                if st.button(f"Save Changes {certification}", key=f"save_cert_{i}"):
                    certifications[i] = new_certification
                    save_data(certifications, './certifications.json')
                    st.success(f'Certification {certification} has been updated!')
                    st.rerun()
                if st.button(f"Delete Certification {certification}", key=f"delete_cert_{i}"):
                    certifications.remove(certification)
                    save_data(certifications, './certifications.json')
                    st.success(f'Certification {certification} has been deleted!')
                    st.rerun()
        new_certification = st.text_input('Add new certification', key='input_certification')
        if st.button('Add Certification', key='submit_certification'):
            if new_certification and new_certification not in certifications:
                certifications.append(new_certification)
                save_data(certifications, './certifications.json')
                st.success(f'Certification {new_certification} has been added!')
                st.rerun()

    elif data_type == "Skills":
        st.subheader("Skills")
        if st.button('Refresh Data'):
            st.rerun()
        skills = load_data('./skills.json')
        for i, skill in enumerate(skills):
            with st.expander(skill):
                new_skill = st.text_input("Edit Skill", value=skill, key=f"edit_skill_{i}")
                if st.button(f"Save Changes {skill}", key=f"save_skill_{i}"):
                    skills[i] = new_skill
                    save_data(skills, './skills.json')
                    st.success(f'Skill {skill} has been updated!')
                    st.rerun()
                if st.button(f"Delete Skill {skill}", key=f"delete_skill_{i}"):
                    skills.remove(skill)
                    save_data(skills, './skills.json')
                    st.success(f'Skill {skill} has been deleted!')
                    st.rerun()
        new_skill = st.text_input('Add new skill', key='input_skill')
        if st.button('Add Skill', key='submit_skill'):
            if new_skill and new_skill not in skills:
                skills.append(new_skill)
                save_data(skills, './skills.json')
                st.success(f'Skill {new_skill} has been added!')
                st.rerun()

    elif data_type == "Projects":
        st.subheader("Projects")
        
        if st.button('Refresh Data'):
            st.rerun()
        
        projects = load_data('./project_data.json')
        
        for i, project in enumerate(projects):
            with st.expander(f"Project Name: {project['project_name']}"):
                new_name = st.text_input(f"Edit Project Name {i}", value=project['project_name'], key=f"edit_proj_name_{i}")
                
                valid_project_certifications = [c for c in certifications_list if c in project['required_certifications']]
                new_certifications = st.multiselect(
                    f"Edit Required Certifications {i}", certifications_list, default=valid_project_certifications, key=f"edit_proj_cert_{i}"
                )
                
                valid_project_skills = [s for s in skills_list if s in project['required_skills']]
                new_skills = st.multiselect(
                    f"Edit Required Skills {i}", skills_list, default=valid_project_skills, key=f"edit_proj_skill_{i}"
                )
                
                if st.button(f"Save Changes {project['project_name']}", key=f"save_proj_changes_{i}"):
                    project['project_name'] = new_name
                    project['required_certifications'] = new_certifications
                    project['required_skills'] = new_skills
                    save_data(projects, './project_data.json')
                    st.success(f'Project {project["project_name"]} has been updated!')
                    st.rerun()
                
                if st.button(f"Delete Project {project['project_name']}", key=f"delete_proj_{i}"):
                    projects.remove(project)
                    save_data(projects, './project_data.json')
                    st.success(f'Project {project["project_name"]} has been deleted!')
                    st.rerun()
        
        new_project_name = st.text_input('Add new project name', key="new_proj_name")
        new_project_certifications = st.multiselect("Add Required Certifications", certifications_list, key="new_proj_cert")
        new_project_skills = st.multiselect("Add Required Skills", skills_list, key="new_proj_skill")
        
        if st.button('Add Project', key="add_proj"):
            if new_project_name:
                new_project = {
                    "project_name": new_project_name,
                    "required_certifications": new_project_certifications,
                    "required_skills": new_project_skills
                }
                projects.append(new_project)
                save_data(projects, './project_data.json')
                st.success(f'Project {new_project_name} has been added!')
                st.rerun()

# Main
worker_vectors = load_data('./employee_data.json')
certifications_list = load_data('./certifications.json')
skills_list = load_data('./skills.json')

# Streamlit sidebar menu
menu = st.sidebar.selectbox("Menu", ["Home", "Search Placement", "Manage Data"])

if menu == "Home":
    Home()
elif menu == "Search Placement":
    search_placement()
elif menu == "Manage Data":
    manage_data()