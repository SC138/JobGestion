import os
import sys
import json
from datetime import datetime
import tkinter as tk
from tkinter import messagebox, filedialog, ttk
from PIL import Image, ImageTk

# Fonction pour obtenir le chemin du fichier ressource
def resource_path(relative_path):
    """ Obtenir le chemin du fichier ressource, en utilisant PyInstaller ou le chemin local. """
    try:
        # PyInstaller crée un dossier temporaire et y stocke les fichiers nécessaires
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)

# Fonction pour sauvegarder les candidatures dans un fichier JSON
def save_applications(database):
    try:
        # Enregistrer dans le répertoire de l'utilisateur
        json_path = os.path.join(os.path.expanduser("~"), "applications.json")
        # Ouvrir le fichier JSON en mode écriture pour y sauvegarder les candidatures
        with open(json_path, "w") as file:
            json.dump(database, file, indent=4)
    except Exception as e:
        # En cas d'erreur, afficher un message d'erreur à l'utilisateur
        messagebox.showerror("Erreur", f"Erreur lors de la sauvegarde des candidatures : {e}")

# Fonction pour lire les candidatures sauvegardées
def load_applications():
    # Charger depuis le répertoire de l'utilisateur
    json_path = os.path.join(os.path.expanduser("~"), "applications.json")
    # Vérifier si le fichier JSON existe
    if os.path.exists(json_path):
        # Si oui, ouvrir le fichier et charger les candidatures
        with open(json_path, "r") as file:
            return json.load(file)
    else:
        # Sinon, retourner une base de données vide
        return {"applications": []}

# Interface utilisateur avec navigation entre les pages
class JobApplicationApp:
    def __init__(self, root):
        # Initialiser la fenêtre principale
        self.root = root
        self.root.title("JobGestion")
        self.root.geometry("1200x800")  # Définir la taille initiale de la fenêtre pour afficher toutes les colonnes
        self.root.minsize(1200, 800)  # Définir la taille minimale de la fenêtre
        self.database = load_applications()  # Charger les candidatures existantes

        # Charger le logo
        logo_path = resource_path("app_logo.png")
        if os.path.exists(logo_path):
            # Si le fichier logo existe, le charger et le redimensionner
            self.logo_image = Image.open(logo_path)
            self.logo_image = self.logo_image.resize((100, 100), Image.LANCZOS)
            self.logo_photo = ImageTk.PhotoImage(self.logo_image)
        else:
            # Si le fichier n'existe pas, afficher un avertissement
            self.logo_photo = None
            messagebox.showwarning("Attention", f"Le fichier app_logo.png est introuvable à l'emplacement : {logo_path}")

        # Charger l'image des flèches pour le tri
        self.sort_arrow_image = None
        arrow_path = resource_path("arrows.png")
        if os.path.exists(arrow_path):
            arrow_image = Image.open(arrow_path).resize((10, 10), Image.LANCZOS)
            self.sort_arrow_image = ImageTk.PhotoImage(arrow_image)

        # Frames pour les différentes pages
        self.home_frame = tk.Frame(self.root, bg='#333333')  # Frame pour la page d'accueil
        self.add_frame = tk.Frame(self.root, bg='#333333')  # Frame pour la page d'ajout/modification

        # Variables de pagination
        self.current_page = 0
        self.items_per_page = 10

        # Variable de tri
        self.sort_by = None
        self.sort_ascending = True

        # Construire la page d'accueil
        self.build_home_page()

        # Construire la page pour ajouter/modifier une candidature
        self.build_add_page()

        # Afficher la page d'accueil par défaut
        self.home_frame.pack(fill='both', expand=True)

    def build_home_page(self):
        # Ajouter le logo si disponible
        if self.logo_photo:
            tk.Label(self.home_frame, image=self.logo_photo, bg='#333333').pack(pady=10)

        # Titre de la page d'accueil
        tk.Label(self.home_frame, text="Vos Candidatures", font=("Helvetica", 16), bg='#333333', fg='#ffffff').pack(pady=10)

        # Barre de recherche dynamique
        self.search_var = tk.StringVar()
        self.search_var.trace("w", self.search_and_update)
        search_entry = tk.Entry(self.home_frame, textvariable=self.search_var, width=40)
        search_entry.pack(pady=5)

        # Frame pour la liste des candidatures
        self.application_list_frame = tk.Frame(self.home_frame, bg='#333333')
        self.application_list_frame.pack(pady=10, padx=10, fill='both', expand=True)

        # Navigation entre les pages
        self.navigation_frame = tk.Frame(self.home_frame, bg='#333333')
        self.navigation_frame.pack(pady=5)

        # Boutons de navigation
        self.prev_page_btn = tk.Button(self.navigation_frame, text="<<", command=self.go_to_first_page, state=tk.DISABLED)
        self.prev_page_btn.grid(row=0, column=0, padx=5)
        self.prev_btn = tk.Button(self.navigation_frame, text="<", command=self.go_to_prev_page, state=tk.DISABLED)
        self.prev_btn.grid(row=0, column=1, padx=5)
        self.page_label = tk.Label(self.navigation_frame, text="Page 1", bg='#333333', fg='#ffffff')
        self.page_label.grid(row=0, column=2, padx=5)
        self.next_btn = tk.Button(self.navigation_frame, text=">", command=self.go_to_next_page)
        self.next_btn.grid(row=0, column=3, padx=5)
        self.next_page_btn = tk.Button(self.navigation_frame, text=">>", command=self.go_to_last_page)
        self.next_page_btn.grid(row=0, column=4, padx=5)

        # Mettre à jour la liste des candidatures
        self.update_application_list()

        # Bouton pour ajouter une nouvelle candidature
        tk.Button(self.home_frame, text="Nouvelle candidature", command=self.switch_to_add_page, bg='#ffffff', fg='#000000', relief=tk.FLAT, highlightthickness=0, cursor="arrow").pack(pady=20)

    def search_and_update(self, *args):
        # Réinitialiser à la première page pour afficher les résultats de recherche
        self.current_page = 0
        self.update_application_list()

    def update_application_list(self, *args):
        # Effacer les widgets existants pour pouvoir recharger la liste
        for widget in self.application_list_frame.winfo_children():
            widget.destroy()

        # Récupérer le texte de recherche
        search_text = self.search_var.get().lower()

        # Filtrer les candidatures selon le texte de recherche
        filtered_apps = [app for app in self.database["applications"] if search_text in app['company_name'].lower() or search_text in app['job_title'].lower()]

        # Trier les candidatures
        if self.sort_by:
            reverse = not self.sort_ascending
            filtered_apps.sort(key=lambda x: x[self.sort_by], reverse=reverse)

        # Pagination
        total_pages = (len(filtered_apps) + self.items_per_page - 1) // self.items_per_page
        start_index = self.current_page * self.items_per_page
        end_index = start_index + self.items_per_page
        current_apps = filtered_apps[start_index:end_index]

        # Mettre à jour l'affichage des pages
        self.page_label.config(text=f"Page {self.current_page + 1} sur {total_pages}")
        self.prev_btn.config(state=tk.NORMAL if self.current_page > 0 else tk.DISABLED)
        self.prev_page_btn.config(state=tk.NORMAL if self.current_page > 0 else tk.DISABLED)
        self.next_btn.config(state=tk.NORMAL if self.current_page < total_pages - 1 else tk.DISABLED)
        self.next_page_btn.config(state=tk.NORMAL if self.current_page < total_pages - 1 else tk.DISABLED)

        # Ajouter un titre de colonne pour améliorer la lisibilité
        headers = ["#", "Entreprise", "Poste", "Date", "Statut", "Actions"]
        for col_num, header in enumerate(headers):
            label = tk.Label(self.application_list_frame, text=header, width=20, font=("Helvetica", 16, "bold"), relief=tk.SOLID, bd=1, bg='#333333', fg='#ffffff', anchor="center")
            label.grid(row=0, column=col_num, sticky="nsew", ipadx=5, ipady=5)
            if header == "Date":
                label.bind("<Button-1>", lambda e: self.sort_by_date())
                tk.Label(self.application_list_frame, image=self.sort_arrow_image, bg='#333333').grid(row=0, column=col_num, sticky="e", ipadx=5, ipady=5)
            elif header == "Statut":
                label.bind("<Button-1>", lambda e: self.sort_by_status())
                tk.Label(self.application_list_frame, image=self.sort_arrow_image, bg='#333333').grid(row=0, column=col_num, sticky="e", ipadx=5, ipady=5)

        # Parcourir chaque candidature dans la base de données
        for idx, app in enumerate(current_apps, start=start_index + 1):
            # Essayer de parser la date dans différents formats
            date_str = app['application_date']
            try:
                date_obj = datetime.strptime(date_str, '%d-%m-%Y')
            except ValueError:
                try:
                    date_obj = datetime.strptime(date_str, '%Y-%m-%d')
                except ValueError:
                    date_obj = None

            # Formater la date pour l'affichage
            formatted_date = date_obj.strftime('%d-%m-%Y') if date_obj else "Date invalide"

            # Couleur en fonction du statut
            status_color = "#ff0000" if app['status'] == "Refusé" else "#00cc66" if app['status'] == "Accepté" else "#0000ff"

            # Ajouter chaque ligne dans le tableau avec les informations sur les candidatures
            tk.Label(self.application_list_frame, text=f"{idx}", width=5, anchor="center", relief=tk.SOLID, bd=1, bg='#333333', fg='#ffffff').grid(row=idx - start_index, column=0, sticky="nsew", ipadx=5, ipady=5)
            tk.Label(self.application_list_frame, text=f"{app['company_name']}", width=20, anchor="w", relief=tk.SOLID, bd=1, bg='#333333', fg='#ffffff').grid(row=idx - start_index, column=1, sticky="nsew", ipadx=5, ipady=5)
            tk.Label(self.application_list_frame, text=f"{app['job_title']}", width=20, anchor="w", relief=tk.SOLID, bd=1, bg='#333333', fg='#ffffff').grid(row=idx - start_index, column=2, sticky="nsew", ipadx=5, ipady=5)
            tk.Label(self.application_list_frame, text=formatted_date, width=10, anchor="center", relief=tk.SOLID, bd=1, bg='#333333', fg='#ffffff').grid(row=idx - start_index, column=3, sticky="nsew", ipadx=5, ipady=5)
            tk.Label(self.application_list_frame, text=f"{app['status']}", width=10, anchor="center", relief=tk.SOLID, bd=1, bg=status_color, fg='#ffffff').grid(row=idx - start_index, column=4, sticky="nsew", ipadx=5, ipady=5)

            # Ajouter un bouton pour modifier ou voir les détails de chaque candidature
            tk.Button(self.application_list_frame, text="Modifier / Voir", command=lambda idx=idx-1: self.edit_application(idx), relief=tk.SOLID, bd=1, bg='#ffffff', fg='#000000', cursor="arrow").grid(row=idx - start_index, column=5, sticky="nsew", ipadx=5, ipady=5)

    def sort_by_date(self):
        if self.sort_by == 'application_date':
            self.sort_ascending = not self.sort_ascending
        else:
            self.sort_by = 'application_date'
            self.sort_ascending = True
        self.update_application_list()

    def sort_by_status(self):
        if self.sort_by == 'status':
            self.sort_ascending = not self.sort_ascending
        else:
            self.sort_by = 'status'
            self.sort_ascending = True
        self.update_application_list()

    def go_to_first_page(self):
        self.current_page = 0
        self.update_application_list()

    def go_to_prev_page(self):
        if self.current_page > 0:
            self.current_page -= 1
            self.update_application_list()

    def go_to_next_page(self):
        self.current_page += 1
        self.update_application_list()

    def go_to_last_page(self):
        filtered_apps = [app for app in self.database["applications"] if self.search_var.get().lower() in app['company_name'].lower() or self.search_var.get().lower() in app['job_title'].lower()]
        total_pages = (len(filtered_apps) + self.items_per_page - 1) // self.items_per_page
        self.current_page = total_pages - 1
        self.update_application_list()

    def switch_to_add_page(self):
        # Passer de la page d'accueil à la page d'ajout en réinitialisant les champs
        self.current_edit_index = None  # Réinitialiser l'index d'édition
        self.company_name_entry.delete(0, tk.END)
        self.job_title_entry.delete(0, tk.END)
        self.cover_letter_entry.delete(0, tk.END)
        self.screenshot_entry.delete(0, tk.END)
        self.status_combobox.current(0)
        self.comment_text.delete('1.0', tk.END)

        self.home_frame.pack_forget()
        self.add_frame.pack(fill='both', expand=True)
        self.root.focus_force()  # Forcer le focus sur la fenêtre principale
        self.root.after(100, lambda: self.add_frame.focus())  # Assurer que le focus est bien sur la fenêtre après un court délai

    def switch_to_home_page(self):
        # Passer de la page d'ajout à la page d'accueil
        self.add_frame.pack_forget()
        self.update_application_list()  # Mettre à jour la liste des candidatures
        self.home_frame.pack(fill='both', expand=True)
        self.root.focus_force()  # Forcer le focus sur la fenêtre principale
        self.root.after(100, lambda: self.home_frame.focus())  # Assurer que le focus est bien sur la fenêtre après un court délai

    def edit_application(self, idx):
        # Charger les informations de la candidature sélectionnée dans les champs
        self.current_edit_index = idx  # Stocker l'index de la candidature en cours d'édition
        selected_application = self.database["applications"][idx]
        self.company_name_entry.delete(0, tk.END)
        self.company_name_entry.insert(0, selected_application["company_name"])
        self.job_title_entry.delete(0, tk.END)
        self.job_title_entry.insert(0, selected_application["job_title"])
        self.cover_letter_entry.delete(0, tk.END)
        self.cover_letter_entry.insert(0, selected_application["cover_letter_path"])
        self.screenshot_entry.delete(0, tk.END)
        self.screenshot_entry.insert(0, selected_application["screenshot_path"])
        self.status_combobox.set(selected_application["status"])
        self.comment_text.delete('1.0', tk.END)
        self.comment_text.insert('1.0', selected_application.get("comment", ""))

        self.home_frame.pack_forget()
        self.add_frame.pack(fill='both', expand=True)
        self.root.focus_force()  # Forcer le focus sur la fenêtre principale
        self.root.after(100, lambda: self.add_frame.focus())  # Assurer que le focus est bien sur la fenêtre après un court délai

    def build_add_page(self):
        # Ajouter le logo centré si disponible
        if self.logo_photo:
            tk.Label(self.add_frame, image=self.logo_photo, bg='#333333').grid(row=0, column=0, columnspan=4, pady=10, sticky='n')

        # Titre de la page d'ajout, centré
        tk.Label(self.add_frame, text="Ajouter / Modifier une Candidature", font=("Helvetica", 16), bg='#333333', fg='#ffffff').grid(row=1, column=0, columnspan=4, pady=10, sticky='n')

        # Champ pour le nom de l'entreprise
        tk.Label(self.add_frame, text="Nom de l'entreprise", bg='#333333', fg='#ffffff').grid(row=2, column=0, padx=10, pady=5, sticky='w')
        self.company_name_entry = tk.Entry(self.add_frame, width=50)
        self.company_name_entry.grid(row=2, column=1, padx=10, pady=5)

        # Champ pour le titre du poste
        tk.Label(self.add_frame, text="Titre du poste", bg='#333333', fg='#ffffff').grid(row=3, column=0, padx=10, pady=5, sticky='w')
        self.job_title_entry = tk.Entry(self.add_frame, width=50)
        self.job_title_entry.grid(row=3, column=1, padx=10, pady=5)

        # Champ pour le chemin de la lettre de motivation
        tk.Label(self.add_frame, text="Chemin de la lettre de motivation", bg='#333333', fg='#ffffff').grid(row=4, column=0, padx=10, pady=5, sticky='w')
        self.cover_letter_entry = tk.Entry(self.add_frame, width=50)
        self.cover_letter_entry.grid(row=4, column=1, padx=10, pady=5)
        tk.Button(self.add_frame, text="Parcourir", command=self.select_cover_letter, cursor="arrow", bg='#ffffff', fg='#000000').grid(row=4, column=2, padx=10, pady=5)
        tk.Button(self.add_frame, text="Voir", command=self.preview_cover_letter, cursor="arrow", bg='#ffffff', fg='#000000').grid(row=4, column=3, padx=10, pady=5)

        # Champ pour le chemin du screenshot de la candidature
        tk.Label(self.add_frame, text="Chemin du screenshot", bg='#333333', fg='#ffffff').grid(row=5, column=0, padx=10, pady=5, sticky='w')
        self.screenshot_entry = tk.Entry(self.add_frame, width=50)
        self.screenshot_entry.grid(row=5, column=1, padx=10, pady=5)
        tk.Button(self.add_frame, text="Parcourir", command=self.select_screenshot, cursor="arrow", bg='#ffffff', fg='#000000').grid(row=5, column=2, padx=10, pady=5)
        tk.Button(self.add_frame, text="Voir", command=self.preview_screenshot, cursor="arrow", bg='#ffffff', fg='#000000').grid(row=5, column=3, padx=10, pady=5)

        # Champ pour le statut de la candidature (En attente, Accepté, Refusé)
        tk.Label(self.add_frame, text="Statut", bg='#333333', fg='#ffffff').grid(row=6, column=0, padx=10, pady=5, sticky='w')
        self.status_combobox = ttk.Combobox(self.add_frame, values=["En attente", "Accepté", "Refusé"], width=47, state='readonly')
        self.status_combobox.grid(row=6, column=1, padx=10, pady=5)
        self.status_combobox.current(0)

        # Champ pour le commentaire de la candidature avec scrollbar
        tk.Label(self.add_frame, text="Commentaire", bg='#333333', fg='#ffffff').grid(row=7, column=0, padx=10, pady=5, sticky='w')
        self.comment_text_frame = tk.Frame(self.add_frame)
        self.comment_text_frame.grid(row=7, column=1, padx=10, pady=5, columnspan=2, sticky='w')
        self.comment_text = tk.Text(self.comment_text_frame, width=67, height=5, wrap='word')
        self.comment_text.pack(side='left', fill='both', expand=True)
        self.comment_scroll = tk.Scrollbar(self.comment_text_frame, command=self.comment_text.yview, width=8)
        self.comment_scroll.pack(side='right', fill='y')
        self.comment_text.config(yscrollcommand=self.comment_scroll.set)

        # Limite de caractères pour le champ commentaire
        self.comment_char_count_label = tk.Label(self.add_frame, text="0/1500", bg='#333333', fg='#ffffff')
        self.comment_char_count_label.grid(row=8, column=1, padx=10, sticky='w')
        self.comment_text.bind("<KeyRelease>", self.update_char_count)

        # Boutons pour sauvegarder la candidature, retourner à la page d'accueil ou supprimer la candidature
        tk.Button(self.add_frame, text="Sauvegarder", command=self.save_application, bg='#ffffff', fg='#000000', relief=tk.RAISED, cursor="arrow").grid(row=9, column=0, pady=20)
        tk.Button(self.add_frame, text="Retour", command=self.switch_to_home_page, bg='#ffffff', fg='#000000', cursor="arrow").grid(row=9, column=1, pady=20)
        tk.Button(self.add_frame, text="Supprimer", command=self.delete_application, bg='#ffffff', fg='#000000', relief=tk.RAISED, cursor="arrow").grid(row=9, column=2, pady=20)

    def update_char_count(self, event):
        current_length = len(self.comment_text.get("1.0", "end-1c"))
        if current_length > 1500:
            self.comment_text.delete("1.0", "end")
            self.comment_text.insert("1.0", event.widget.get("1.0", "end-1c")[:1500])
            current_length = 1500
        self.comment_char_count_label.config(text=f"{current_length}/1500")

    def save_application(self):
        # Récupérer les informations des champs
        company_name = self.company_name_entry.get().strip()
        job_title = self.job_title_entry.get().strip()
        cover_letter_path = self.cover_letter_entry.get().strip()
        screenshot_path = self.screenshot_entry.get().strip()
        status = self.status_combobox.get()
        comment = self.comment_text.get('1.0', tk.END).strip()

        # Vérifier que tous les champs sont remplis
        if not company_name or not job_title or not cover_letter_path or not screenshot_path:
            messagebox.showerror("Erreur", "Tous les champs doivent être remplis.")
            return

        # Mise à jour ou ajout de la candidature
        if self.current_edit_index is not None:
            # Mise à jour de la candidature existante
            self.database["applications"][self.current_edit_index]["company_name"] = company_name
            self.database["applications"][self.current_edit_index]["job_title"] = job_title
            self.database["applications"][self.current_edit_index]["cover_letter_path"] = cover_letter_path
            self.database["applications"][self.current_edit_index]["screenshot_path"] = screenshot_path
            self.database["applications"][self.current_edit_index]["status"] = status
            self.database["applications"][self.current_edit_index]["comment"] = comment
        else:
            # Ajouter une nouvelle candidature
            application = {
                "company_name": company_name,
                "job_title": job_title,
                "cover_letter_path": cover_letter_path,
                "screenshot_path": screenshot_path,
                "application_date": datetime.now().strftime("%d-%m-%Y"),
                "status": status,
                "comment": comment
            }
            self.database["applications"].append(application)

        # Sauvegarder les changements dans le fichier JSON
        save_applications(self.database)
        messagebox.showinfo("Succès", "Candidature sauvegardée avec succès.")
        self.switch_to_home_page()

    def delete_application(self):
        # Supprimer la candidature actuellement sélectionnée
        if self.current_edit_index is not None:
            confirm = messagebox.askyesno("Confirmation", "Voulez-vous vraiment supprimer cette candidature ?")
            if confirm:
                del self.database["applications"][self.current_edit_index]
                save_applications(self.database)
                messagebox.showinfo("Succès", "Candidature supprimée avec succès.")
                self.switch_to_home_page()
        else:
            messagebox.showerror("Erreur", "Aucune candidature sélectionnée pour la suppression.")

    def select_cover_letter(self):
        # Ouvrir une boîte de dialogue pour sélectionner le fichier de la lettre de motivation
        file_path = filedialog.askopenfilename(title="Sélectionner la lettre de motivation", filetypes=[("Documents PDF", "*.pdf"), ("Fichiers texte", "*.txt")])
        if file_path:
            self.cover_letter_entry.delete(0, tk.END)
            self.cover_letter_entry.insert(0, file_path)

    def select_screenshot(self):
        # Ouvrir une boîte de dialogue pour sélectionner le fichier du screenshot
        file_path = filedialog.askopenfilename(title="Sélectionner le screenshot", filetypes=[("Images", "*.png"), ("Images", "*.jpg"), ("Images", "*.jpeg")])
        if file_path:
            self.screenshot_entry.delete(0, tk.END)
            self.screenshot_entry.insert(0, file_path)

    def preview_cover_letter(self):
        # Ouvrir le fichier de la lettre de motivation avec l'application par défaut
        file_path = self.cover_letter_entry.get()
        if os.path.exists(file_path):
            os.system(f"open '{file_path}'")
        else:
            messagebox.showerror("Erreur", "Le fichier spécifié est introuvable.")

    def preview_screenshot(self):
        # Ouvrir une fenêtre de prévisualisation pour le screenshot
        file_path = self.screenshot_entry.get()
        if os.path.exists(file_path):
            try:
                img = Image.open(file_path)
                img = img.resize((300, 300))
                img_tk = ImageTk.PhotoImage(img)
                preview_window = tk.Toplevel(self.root)
                preview_window.title("Aperçu du Screenshot")
                tk.Label(preview_window, image=img_tk).pack()
                preview_window.mainloop()
            except Exception as e:
                messagebox.showerror("Erreur", f"Impossible d'ouvrir l'image : {e}")
        else:
            messagebox.showerror("Erreur", "Le fichier spécifié est introuvable.")

# Créer la fenêtre principale Tkinter et lancer l'application
root = tk.Tk()
app = JobApplicationApp(root)
root.mainloop()
