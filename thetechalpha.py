import tkinter as tk
from tkinter import scrolledtext
import difflib
import os

class TheTechAlphaBot:
    def __init__(self, root):
        self.root = root
        self.root.title("The Tech Alpha - AI Chatbot Support")
        self.root.geometry("450x650")
        self.root.configure(bg="#f4f6f9")
        self.company_name = "The Tech Alpha"
        self.university_name = "CSJM University (CSJMU)"
        self.qa_database = {
            "1": {
                "question": "When do admissions start at CSJM University?",
                "keywords": ["admission", "start", "एडमिशन", "कब", "form"],
                "answer": "Admissions at Chhatrapati Shahu Ji Maharaj University (CSJMU) generally start in April each year.The admission window remains active for several months depending on whether the course is based on direct merit or entrance exams. Below is a timeline of the admission schedule:"
                "📅 General Admission TimelineRelease of Application Forms: The online application registration starts between early April and May.Entrance Exams & Counseling: For specialized programs (like MBA, B.Tech, MCA, LLM, or M.Ed), university-level entrance tests and subsequent counseling typically take place in May, June, or July.Normal Registration Deadline: For regular merit-based UG and PG courses, the standard registration window usually runs until late July or August.Extended Admissions (With Late Fee / Distance Learning): The university often extends application lines or opens distinct cycles for Open & Distance Learning (ODL) options through September."
                "📝 Admission CriteriaMerit-Based: For standard courses like BA, B.Sc, B.Com, and MA, admissions are granted directly based on your marks in 10+2 or graduation.Entrance Exam-Based: Professional courses rely either on the CSJMU Admission Portal internal tests or national/state exams (such as JEE Main for B.Tech, NEET for MBBS, or CUET)."
            },
            "2": {
                "question": "Which courses are available at CSJM University?",
                "keywords": ["course", "programs", "कोर्स", "branch", "स्ट्रीम"],
                "answer": "Chhatrapati Shahu Ji Maharaj University (CSJMU), formerly known as Kanpur University, offers a diverse selection of undergraduate (UG), postgraduate (PG), diploma, and doctoral (PhD) programs across multiple fields of study.The extensive list of courses available at CSJMU is categorized below by stream:"
                "🛠️ Engineering & TechnologyEngineering & Computing: B.Tech (Chemical, CSE, AI, ECE, IT, Mechanical, Metallurgical), BCA, MCA, and M.Sc. in Computer Science/IT."
                "💼 Business, Commerce & ManagementManagement & Commerce: MBA (Full-time & Part-time), BBA, B.Com (Regular & Hons.), and Master of Rural Management & Extension."
                "🩺 Health Sciences, Pharmacy & MedicineMedical, Paramedical & Nursing: Programs include Pharmacy (B.Pharm, D.Pharm), MBBS/BDS/BAMS via affiliates, Allied Health (BPT, Optometry, MLT), Nursing, and M.Sc. Human Nutrition."
                "🔬 Basic & Life SciencesSciences: B.Sc. (Hons.) and M.Sc. across Physics, Chemistry, Mathematics, Environmental Science, Biochemistry, Microbiology, and Integrated Biotechnology/Microbiology."
                "🌾 AgricultureAgricultural Sciences: B.Sc. (Hons.) Agriculture and M.Sc. (Ag) in Agronomy, Horticulture, and Food Science.⚖️ LawLegal Studies: Integrated B.A. L.L.B. (Hons.), B.B.A. L.L.B. (Hons.), and L.L.M.."
                "🎨 Arts, Humanities & Social SciencesHumanities & Media: B.A. and M.A. in subjects like English, Psychology, and Journalism, alongside Library Sciences and Performing Arts (Theatre, Dance, Music)."
                "📜 Vocational, Diploma & Doctoral ProgramsOther Programs: B.Voc, Education degrees (B.Ed, M.Ed, B.P.Ed), diverse diplomas/certificates (languages, hospitality, media), and PhD programs across major disciplines."
            },
            "3": {
                "question": "Provide the detailed fee structure for all courses of CSJMU.",
                "keywords": ["fees", "fee", "structure", "फीस", "खर्चा", "पैसा"],
                "answer": "Chhatrapati Shahu Ji Maharaj University (CSJMU) offers courses ranging from highly affordable conventional degrees to self-financed professional programs.The annual academic fee structure for the most popular courses running on the main university campus is outlined below:"
                "🏢 Engineering & TechnologyB.Tech (CSE / AI): ₹1,15,200 per yearB.Tech (Other streams like Chemical, Mechanical): ₹80,000 – ₹90,200 per yearBCA: ₹55,200 per yearMCA: ₹50,000 – ₹60,000 per year"
                "💼 Management & CommerceMBA (Regular): ₹90,200 per yearBBA: ₹45,000 – ₹50,000 per yearB.Com (Hons): ₹25,000 – ₹30,000 per year🔬 Basic & Life SciencesB.Sc. (Hons. Physics/Chemistry/Maths): ₹34,400 per yearB.Sc. (Biotechnology): Starts around ₹30,200 for the 1st yearM.Sc. (Regular streams): ₹15,000 – ₹35,000 per year"
                "⚖️ LawB.A. LL.B. (Hons): ₹66,200 per yearBBA LL.B. (Hons): ₹71,200 per year🎨 Arts & HumanitiesB.A. (Hons): ₹26,200 per yearM.A. (Economics/Sociology/English): ₹10,200 – ₹15,000 per year"
                "🩺 Paramedical & PharmacyB.Pharm / D.Pharm: ₹60,000 – ₹80,000 per yearBPT / Allied Health: ₹50,000 – ₹70,000 per year"
                "📜 Short-term Diplomas & CertificatesUG/PG Diplomas: ₹15,000 – ₹35,000 (Total course fee)Certificate Courses: ₹6,600 – ₹25,500 (Total course fee)"
            },
            "4": {
                "question": "What is the placement record of CSJMU for the last 5 years?",
                "keywords": ["placement", "job", "salary", "पैकेज", "प्लेसमेंट", "कंपनी"],
                "answer": "Here is the untabulated, descriptive breakdown of Chhatrapati Shahu Ji Maharaj University (CSJMU) placement records and highlights for the last five years:"
                "📈 Year-by-Year Placement BreakdownAcademic Year 2025–2026Highest Package: The highest package reached ₹16.5 LPA.Median Salary: The overall median package stood at ₹4.0 LPA.Highlights: The highest package witnessed a major 65% jump compared to the previous year. The Information Technology (IT) branch recorded a stellar 89% placement rate.Academic Year 2024–2025Highest Package: The highest domestic package secured was ₹12.5 LPA.Average Salary: The overall campus average was ₹3.20 LPA.Highlights: More than 440+ students were successfully placed on campus, with B.Tech Computer Science Engineering (CSE) students securing top-tier offers from companies like Samsung.Academic Year 2023–2024Highest Package: The university recorded a peak package of ₹18.0 LPA.Average Salary: The median salary was ₹3.50 LPA for 4-year undergraduate programs and ₹6.0 LPA for postgraduate students.Highlights: According to official NIRF data, a total of 652 UG and 311 PG students successfully transitioned into corporate jobs.Academic Year 2022–2023Highest Package: The highest package recorded on campus was ₹10.0 LPA.Average Salary: B.Tech graduates received an average of ₹4.09 LPA, while MBA graduates secured an average of ₹3.20 LPA.Highlights: Strong hiring momentum in core engineering and management streams resulted in a total of 612 distinct campus job offers.Academic Year 2021–2022Highest Package: The highest package during this period was ₹7.0 LPA.Average Salary: The overall campus average sat at ₹3.00 LPA.Highlights: Marked a healthy post-pandemic recovery with companies hiring heavily in mass technology, software services, and sales domains."
                "🏢 Key Course Trends & Top RecruitersEngineering & IT (B.Tech, BCA, MCA): Computer Science and IT remain the top-performing departments, routinely achieving 85% to 95% placement rates. MCA students generally outpace BCA students with packages climbing up to ₹7.2 LPA.Management (MBA & BBA): Packages fluctuate between ₹3.0 LPA to ₹8.0 LPA, with recruitment heavily focused on digital marketing, banking, retail management, and corporate sales.Major Recruiter Networks: Over these five years, the university placement cell has brought in tech giants like TCS, Infosys, Wipro, HCL, and IBM, alongside corporate firms like Samsung, Amazon, Flipkart, HDFC Bank, and Aditya Birla Group."
            },
            "5": {
                "question": "Does CSJMU provide hostel facilities?",
                "keywords": ["hostel", "accommodation", "हॉस्टल", "रहने", "कमरा"],
                "answer": "Chhatrapati Shahu Ji Maharaj University (CSJMU) offers safe and well-managed residential facilities on its main campus. The campus has 6 on-campus hostels with a total accommodation capacity of 1,114 students.The full overview of the hostel infrastructure, dining, amenities, and regulations at CSJMU is detailed below:"
                "🏢 Hostel Layout & DistributionThe hostels provide shared accommodation consisting primarily of 2-seater (double sharing) and 3-seater (triple sharing) rooms, fully equipped with individual beds, study tables, chairs, and wardrobes:Boys' Hostels (Total 2):Shivaji Boys Hostel (400 seats)Swarn Jayanti Boys Hostel (200 seats)Girls' Hostels (Total 4):Saraswati Girls Hostel (218 seats)Kaveri Girls Hostel (116 seats)Triveni Girls Hostel (108 seats)Ganga Girls Hostel (72 seats – exclusively reserved for EWS students)"
                "🍽️ Mess & Food FacilitiesMeal Structure: The university mess provides 4 meals a day, including breakfast, lunch, evening tea/snacks, and dinner.Menu & Quality: The menu is monitored and modified weekly by a joint student-led Mess Committee and the Hostel Warden to track hygiene standards.Cost: While basic room rents range between ₹17,000 to ₹31,000 annually, the mandatory mess operations cost approximately ₹48,000 per year."
                "⚡ General Amenities & Campus SupportUtilities: Residents get 24-hour electricity backup, running water supply, water coolers with RO purification, and active geyser facilities during winter.Connectivity & Entertainment: High-speed Wi-Fi access is available across the blocks. Hostels feature a common room with a television, daily newspapers, and magazines.Fitness & Sports: There are dedicated on-campus gym facilities accessible to both male and female hostellers, alongside a badminton court and access to the main university sports complex.Health & Safety: The campus features round-the-clock security with CCTV surveillance at all entry/exit gates. A 10-bed University Health Centre operates on-campus with specialist doctors and a 24/7 emergency ambulance service."
                "⚖️ Rules and Strict GuidelinesCurfew Timings: The university maintains a strict discipline framework. The standard outing timing for hostellers is from 6:00 AM to 7:00 PM.Attendance Check: In the girls' hostels, a mandatory roll-call is taken every evening at 9:00 PM. No student is allowed outside the gates past this hour without prior written permission from the warden.Strict Prohibitions: Consumption of alcohol, smoking, or creating noise disruptions inside the rooms carries steep disciplinary actions and heavy fines."
            }
        }
        
        self.setup_ui()
        
    def setup_ui(self):
        header = tk.Label(self.root, text=self.company_name.upper(), font=("Arial", 40, "bold"), bg="#686b6f", fg="#46297b", padx=10, pady=10)
        header.pack(fill=tk.X)
        
        subheader = tk.Label(self.root, text=f"Knowledge Base: {self.university_name} Info", font=("Helvetica", 12, "italic"), bg="#8F949B", fg="#060c14", padx=4, pady=4)
        subheader.pack(fill=tk.X)
        
        suggest_frame = tk.LabelFrame(self.root, text=" 📌 Quick Options (Select to ask from here) ", font=("Arial", 20, "bold"), bg="#f4f6f9", fg="#030810", padx=10, pady=5)
        suggest_frame.pack(fill=tk.X, padx=10, pady=5)
        
        for key, val in self.qa_database.items():
            lbl = tk.Label(suggest_frame, text=f"[{key}] {val['question']}", font=("Arial", 10), bg="#f4f6f9", anchor="w", fg="#05090E")
            lbl.pack(fill=tk.X)

        chat_container = tk.Frame(self.root, bg="white")
        chat_container.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

        image_path = "logo.png"
        if os.path.exists(image_path):
            try:
                self.bg_image = tk.PhotoImage(file=image_path)
                bg_label = tk.Label(chat_container, image=self.bg_image, bg="white")
                bg_label.place(relx=0.5, rely=0.5, anchor=tk.CENTER)
            except Exception as e:
                print(f"इमेज लोड करने में समस्या: {e}. कृपया सुनिश्चित करें कि यह एक वैध .png फ़ाइल है।")

        self.chat_area = scrolledtext.ScrolledText(chat_container, font=("Helvetica", 10), state='disabled', wrap=tk.WORD, bg="white", bd=0, highlightthickness=0)
        self.chat_area.pack(fill=tk.BOTH, expand=True)
        self.display_bot_message(f"Hello! I'm The tech alpha virtual assistant. please type a number (1-5) or reply with keywords to ask your question.")

        input_frame = tk.Frame(self.root, bg="#f4f6f9")
        input_frame.pack(fill=tk.X, padx=10, pady=10)
        
        self.entry_box = tk.Entry(input_frame, font=("Helvetica", 11), bd=1, relief=tk.SOLID)
        self.entry_box.pack(side=tk.LEFT, fill=tk.X, expand=True, ipady=6, padx=(0, 5))
        self.entry_box.bind("<Return>", lambda event: self.process_message())
        
        send_btn = tk.Button(input_frame, text="Send", font=("Helvetica", 10, "bold"), bg="#09090a", fg="black", relief=tk.FLAT, command=self.process_message, width=8)
        send_btn.pack(side=tk.RIGHT, ipady=4)

    def display_bot_message(self, text):
        self.chat_area.config(state='normal')
        self.chat_area.insert(tk.END, "🤖 CHATBOT :\n" + text + "\n\n", "bot")
        self.chat_area.tag_config("bot", foreground="#050709", font=("Helvetica", 10, "bold"))
        self.chat_area.config(state='disabled')
        self.chat_area.yview(tk.END)

    def display_user_message(self, text):
        self.chat_area.config(state='normal')
        self.chat_area.insert(tk.END, "🧑 YOU: " + text + "\n", "user")
        self.chat_area.tag_config("user", foreground="#0f766e")
        self.chat_area.config(state='disabled')
        self.chat_area.yview(tk.END)

    def process_message(self):
        user_text = self.entry_box.get().strip()
        if not user_text:
            return
            
        self.display_user_message(user_text)
        self.entry_box.delete(0, tk.END)
        
        response = self.match_response(user_text.lower())
        self.root.after(400, lambda: self.display_bot_message(response))

    def match_response(self, text):
        if text in self.qa_database:
            return self.qa_database[text]["answer"]
        words = text.split()
        for key, data in self.qa_database.items():
            for keyword in data["keywords"]:
                matches = difflib.get_close_matches(keyword, words, n=1, cutoff=0.7)
                if matches or keyword in text:
                    return data["answer"]
                    
        return "I'm sorry, I didn't quite catch that. Please select a topic (1-5) from the list above to proceed."

if __name__ == "__main__":
    root = tk.Tk()
    app = TheTechAlphaBot(root)
    root.mainloop()
