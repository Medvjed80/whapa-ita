#!/usr/bin/python3
# -*- coding: utf-8 -*-
"""
whapa-gui.py - Interfaz grafica de WhaPa (CustomTkinter)

COMETIDO DE ESTE ARCHIVO
    Ser un lanzador de las herramientas de libs/, no una reimplementacion de
    ellas. Cada pestana corresponde a un archivo y compone sus argumentos:

        WhaPa      -> libs/whapa.py      analisis de la base de datos
        WhaCipher  -> libs/whacipher.py  descifrado y cifrado
        WhaMerge   -> libs/whamerge.py   fusion de bases
        WhaGoDri   -> libs/whagodri.py   descarga desde Google Drive
        WhaChat    -> libs/whachat.py    analisis de chats exportados
        WhaCloud   -> libs/whacloud.py   descarga desde iCloud

QUE CAMBIA RESPECTO A LA VERSION ANTERIOR
    * Reescrita con CustomTkinter (tema oscuro), compatible con Python 3.11+.
    * Las ordenes se lanzan con subprocess y una LISTA de argumentos, no con
      os.system() sobre una cadena montada a mano: aquello permitia inyeccion
      de ordenes a traves de los nombres de archivo.
    * La ejecucion corre en un hilo aparte y la salida se vuelca en directo en
      el panel inferior, de modo que la ventana no se congela.
    * Todo acceso a los widgets ocurre en el hilo principal (Tkinter no es
      seguro entre hilos); el hilo de trabajo solo escribe en una cola.

Requisitos:  pip install customtkinter

** Author: Ivan Moreno a.k.a B16f00t
** Github: https://github.com/B16f00t
"""

import os
import sys
import queue
import shlex
import threading
import subprocess
import webbrowser
from configparser import ConfigParser

try:
    import customtkinter as ctk
    from tkinter import filedialog, messagebox
except ImportError:
    sys.exit("customtkinter is missing. Install it with:  pip install customtkinter")

APP_DIR = os.path.dirname(os.path.abspath(__file__))
LIBS = os.path.join(APP_DIR, "libs")
version = "2.00"

ACCENT, ACCENT_HOVER = "#00a884", "#01976e"
BG, PANEL, FIELD = "#0b141a", "#111b21", "#202c33"
MUTED, TEXT, ERROR = "#8696a0", "#e9edef", "#f15c6d"


# ===========================================================================
#  Idiomas de la interfaz
# ===========================================================================
LANG = {
 "IT": {
  "subtitle": "Analisi forense di WhatsApp - Android e iOS",
  "output": "Output", "clear": "Pulisci", "browse": "Sfoglia",
  "deps": "Installa dipendenze", "settings": "Impostazioni",
  "readme": "Manuale", "about": "Informazioni", "lang": "English",
  "run": "Esegui", "hint_start": "Scegli una scheda, compila i campi e premi il pulsante dell'azione.",
  "db": "Database", "db_dec": "Database decifrato", "contacts": "Contatti (opzionale)",
  "contacts_txt": "Rubrica telefonica (txt)",
  "outdir": "Cartella di output", "wafolder": "Cartella WhatsApp (opzionale)",
  "copymedia": "Copia gli allegati nel rapporto (unico pacchetto consegnabile)",
  "mode": "Modalita", "platform": "Piattaforma", "auto": "Rilevamento automatico",
  "m_msg": "Messaggi", "m_status": "Info: stati", "m_calls": "Info: chiamate",
  "m_chats": "Info: chat attive", "m_extract": "Estrai allegati", "m_carving": "Carving",
  "recipients": "Destinatari", "scope": "Ambito", "all": "Tutti", "user": "Utente",
  "group": "Gruppo", "byuser": "Messaggi da un numero", "broadcast": "Trasmissione",
  "target": "Numero o gruppo", "filters": "Filtri", "text": "Testo",
  "sender": "Mittente", "from": "Da", "to": "A", "rawtypes": "Codici nativi",
  "direction": "Direzione", "d_all": "Tutte", "d_sent": "Inviati",
  "d_recv": "Ricevuti", "d_sys": "Di sistema",
  "searchopts": "OPZIONI DI RICERCA", "types": "TIPI DI MESSAGGIO (se non ne selezioni nessuno, sono inclusi tutti)",
  "outsec": "Output", "report": "Rapporto interattivo", "none": "Nessuno",
  "print": "Rapporto stampabile", "csv": "Esporta CSV", "kml": "Esporta posizioni in KML",
  "maps": "Scarica mappe (richiede Internet)", "single": "Rapporto in un singolo file",
  "pack": "Esporta chat selezionata (HTML/PDF in tar.gz)",
  "warn_pack": "Per impacchettare una sola chat scegli Ambito = Utente o Gruppo e indica il numero.",
  "cipher_sec": "Decifratura e cifratura dei database", "action": "Azione",
  "decrypt": "Decifra", "encrypt": "Cifra (crypt15)", "input": "File di input",
  "isdir": "L'input e una cartella (solo decifratura)", "key": "Chiave",
  "keyhint": "La chiave puo essere il file .key, encrypted_backup.key o i 64 caratteri esadecimali della chiave radice.",
  "outfile": "Output", "merge_sec": "Unione dei database",
  "mergefolder": "Cartella con i database", "mergeout": "Database risultante",
  "gd_sec": "Google Drive", "gd_cred": "Le credenziali vengono lette da cfg/settings.cfg, sezione [google-auth].",
  "gd_info": "Informazioni sui backup", "gd_list": "Elenca tutto", "gd_listwa": "Elenca backup WhatsApp",
  "gd_pull": "Scarica un file", "gd_sync": "Sincronizza tutto", "gd_img": "Solo immagini",
  "gd_vid": "Solo video", "gd_aud": "Solo audio", "gd_doc": "Solo documenti", "gd_db": "Solo database",
  "remotefile": "File da scaricare", "threads": "Thread",
  "noparallel": "Nessun download parallelo", "dryrun": "Simulazione (nessun download)",
  "chat_sec": "Chat esportata dall'applicazione", "chatfile": "File della chat",
  "system": "Sistema", "chatuser": "Utente destinatario", "datemask": "Maschera data",
  "onlypart": "Elenca solo i partecipanti", "ic_sec": "iCloud",
  "chatmedia": "Cartella con gli allegati esportati",
  "copymedia_short": "Copia allegati nel rapporto", "regex": "Regex",
  "ic_cred": "Le credenziali vengono lette da cfg/settings.cfg, sezione [icloud-auth].",
  "ic_list": "Elenca", "ic_sync": "Sincronizza tutto", "ic_img": "Solo immagini",
  "ic_vid": "Solo video e audio",
  "cfg_title": "Impostazioni", "cfg_report": "Dati del rapporto",
  "cfg_google": "Google Drive", "cfg_icloud": "iCloud", "cfg_save": "Salva",
  "cfg_cancel": "Annulla", "cfg_saved": "Impostazioni salvate in cfg/settings.cfg",
  "cfg_company": "Azienda / Ente", "cfg_record": "Riferimento del procedimento",
  "cfg_unit": "Unita", "cfg_examiner": "Analista / operatore", "cfg_notes": "Note",
  "cfg_gmail": "Account Gmail", "cfg_password": "Password (o password app se usi 2FA)",
  "cfg_oauth": "Cookie oauth (opzionale)", "cfg_android_id": "android_id",
  "cfg_celnumbr": "Numeri da sincronizzare (opzionale)",
  "cfg_icloud_user": "Account iCloud", "cfg_icloud_pass": "Password",
  "deps_title": "Installa dipendenze",
  "deps_q": "Verranno installate le dipendenze di doc/requirements.txt.\n\nServe una connessione Internet e l'operazione puo richiedere tempo.\n\nContinuare?",
  "missing": "Dipendenze mancanti", "allok": "Tutte le dipendenze sono installate.",
  "ph_db": "msgstore.db (Android)  /  ChatStorage.sqlite (iOS)",
  "ph_wa": "wa.db (Android)  /  ContactsV2.sqlite (iOS)  -  aggiunge i nomi",
  "ph_ct": "Contatos.txt  -  display_name=Nome, data1=numero",
  "ph_enc": "msgstore.db.crypt15  /  .crypt14  /  .crypt12",
  "ph_key": "file key  /  encrypted_backup.key  /  64 caratteri hex",
  "ph_out": "cartella in cui salvare il rapporto",
  "ph_outfile": "msgstore.db  (file da creare)",
  "ph_media": "cartella WhatsApp copiata dal telefono (quella che contiene Media)",
  "ph_chat": "Chat WhatsApp con <nome>.txt",
  "ph_chatmedia": "per impostazione predefinita, la stessa cartella del .txt",
  "ph_mergedir": "cartella con piu msgstore.db",
  "ph_mergeout": "msgstore_merge.db  (file da creare)",
  "ph_cipher_in": "Database cifrato o decifrato", "ph_keyfile": "File chiave",
  "ph_cipher_out": "File o cartella di output", "ph_merge_folder": "Cartella con msgstore*.db",
  "ph_content": "contenuto, file o citazione", "ph_sender_hint": "numero o nome",
  "ph_user_shown": "nome esattamente come appare", "ph_remote": "percorso remoto",
  "ph_chat_export": "Chat esportata (.txt)", "all_files": "Tutti",
  "plat_android": "Android attuale", "plat_android_legacy": "Android legacy",
  "f_case": "Maiuscole/minuscole", "f_word": "Parola intera", "f_web": "WhatsApp Web",
  "f_starred": "In evidenza", "f_forwarded": "Inoltrati", "f_edited": "Modificati",
  "f_media": "Con allegato", "f_location": "Con coordinate",
  "f_read": "Letti", "f_unread": "Senza conferma di lettura",
  "ty_text": "Testo", "ty_image": "Immagine", "ty_audio": "Audio", "ty_video": "Video",
  "ty_contact": "Contatto", "ty_loc": "Posizione", "ty_call": "Chiamata",
  "ty_doc": "Documento", "ty_gif": "GIF", "ty_deleted": "Eliminato",
  "ty_live": "Posizione in tempo reale", "ty_sticker": "Sticker", "ty_sys": "Sistema",
  "ty_poll": "Sondaggio", "ty_viewonce": "Visualizzazione unica", "ty_note": "Nota video",
  "ty_event": "Evento",
  "ph_case": "Procedimento 1234/2026  -  apparira in copertina",
  "ph_examiner": "chi firma l'analisi",
  "warn_data": "Dati mancanti", "warn_db": "Scegli un database.",
  "warn_in": "Input, chiave e output sono obbligatori.",
  "warn_folder": "Scegli la cartella con i database.", "warn_chat": "Scegli il file della chat.",
  "warn_remote": "Indica il file da scaricare.", "warn_file": "Indica il file.",
  "not_found": "Non trovato {}", "ft_text": "Testo", "ft_db": "Database",
  "ic_pull": "Scarica un file",
  "fin_ok": "Processo terminato correttamente.",
  "fin_code": "Processo terminato con codice {}.",
  "err_exec": "Impossibile eseguire: {}",
  "license": "Licenza GPL-3.0",
  "import_ctk": "Manca customtkinter. Installalo con: pip install customtkinter",
  "warn_wrong_db_wa": "Sembra wa.db (contatti), non msgstore.db (messaggi).\n\nNel campo Database usa msgstore.db decifrato.\nwa.db va solo in Contatti (opzionale).",
  "warn_wrong_db": "Database non riconosciuto.\n\nWhaPa analizza:\n- Android: msgstore.db (decifrato)\n- iOS: ChatStorage.sqlite\n\nwa.db serve solo per i nomi dei contatti.",
 },
 "ES": {
  "subtitle": "Analisis forense de WhatsApp - Android e iOS",
  "output": "Salida", "clear": "Limpiar", "browse": "Examinar",
  "deps": "Instalar dependencias", "settings": "Configuracion",
  "readme": "Manual", "about": "Acerca de", "lang": "Italiano",
  "run": "Ejecutar", "hint_start": "Elige una pestana, completa los campos y pulsa el boton de accion.",
  "db": "Base de datos", "db_dec": "Base descifrada", "contacts": "Contactos (opcional)",
  "contacts_txt": "Agenda telefonica (txt)",
  "outdir": "Carpeta de salida", "wafolder": "Carpeta WhatsApp (opcional)",
  "copymedia": "Copiar los adjuntos dentro del informe (entregable en un solo paquete)",
  "mode": "Modo", "platform": "Plataforma", "auto": "Autodetectar",
  "m_msg": "Mensajes", "m_status": "Info: estados", "m_calls": "Info: llamadas",
  "m_chats": "Info: chats activos", "m_extract": "Extraer adjuntos", "m_carving": "Carving",
  "recipients": "Destinatarios", "scope": "Alcance", "all": "Todos", "user": "Usuario",
  "group": "Grupo", "byuser": "Mensajes de un numero", "broadcast": "Difusion",
  "target": "Numero o grupo", "filters": "Filtros", "text": "Texto",
  "sender": "Remitente", "from": "Desde", "to": "Hasta", "rawtypes": "Codigos nativos",
  "direction": "Direccion", "d_all": "Todas", "d_sent": "Enviados",
  "d_recv": "Recibidos", "d_sys": "Del sistema",
  "searchopts": "OPCIONES DE BUSQUEDA", "types": "TIPOS DE MENSAJE (si no marcas ninguno, se incluyen todos)",
  "outsec": "Salida", "report": "Informe interactivo", "none": "Ninguno",
  "print": "Informe imprimible", "csv": "Exportar CSV", "kml": "Exportar ubicaciones a KML",
  "maps": "Descargar mapas (necesita internet)", "single": "Informe en un solo archivo",
  "pack": "Exportar chat seleccionado (tar.gz)",
  "warn_pack": "Para empaquetar un solo chat elige Ambito = Usuario o Grupo e indica el numero.",
  "cipher_sec": "Descifrado y cifrado de bases de datos", "action": "Accion",
  "decrypt": "Descifrar", "encrypt": "Cifrar (crypt15)", "input": "Archivo de entrada",
  "isdir": "La entrada es un directorio (solo descifrado)", "key": "Clave",
  "keyhint": "La clave puede ser el archivo .key, encrypted_backup.key o los 64 caracteres hexadecimales de la clave raiz.",
  "outfile": "Salida", "merge_sec": "Fusion de bases de datos",
  "mergefolder": "Carpeta con las bases", "mergeout": "Base resultante",
  "gd_sec": "Google Drive", "gd_cred": "Las credenciales se leen de cfg/settings.cfg, seccion [google-auth].",
  "gd_info": "Informacion de copias", "gd_list": "Listar todo", "gd_listwa": "Listar copias de WhatsApp",
  "gd_pull": "Descargar un archivo", "gd_sync": "Sincronizar todo", "gd_img": "Solo imagenes",
  "gd_vid": "Solo videos", "gd_aud": "Solo audios", "gd_doc": "Solo documentos", "gd_db": "Solo bases",
  "remotefile": "Archivo a descargar", "threads": "Hilos",
  "noparallel": "Sin descargas en paralelo", "dryrun": "Simulacion (no descarga)",
  "chat_sec": "Chat exportado desde la aplicacion", "chatfile": "Archivo del chat",
  "system": "Sistema", "chatuser": "Usuario destinatario", "datemask": "Mascara de fecha",
  "onlypart": "Solo listar participantes", "ic_sec": "iCloud",
  "chatmedia": "Carpeta con los adjuntos exportados",
  "copymedia_short": "Copiar adjuntos al informe", "regex": "Regex",
  "ic_cred": "Las credenciales se leen de cfg/settings.cfg, seccion [icloud-auth].",
  "ic_list": "Listar", "ic_sync": "Sincronizar todo", "ic_img": "Solo imagenes",
  "ic_vid": "Solo videos y audios",
  "cfg_title": "Configuracion", "cfg_report": "Datos del informe",
  "cfg_google": "Google Drive", "cfg_icloud": "iCloud", "cfg_save": "Guardar",
  "cfg_cancel": "Cancelar", "cfg_saved": "Configuracion guardada en cfg/settings.cfg",
  "cfg_company": "Empresa / Organismo", "cfg_record": "Referencia del atestado",
  "cfg_unit": "Unidad", "cfg_examiner": "Instructor / analista", "cfg_notes": "Notas",
  "cfg_gmail": "Cuenta de Gmail", "cfg_password": "Contrasena (o de aplicacion si usas 2FA)",
  "cfg_oauth": "Cookie oauth (opcional)", "cfg_android_id": "android_id",
  "cfg_celnumbr": "Numeros a sincronizar (opcional)",
  "cfg_icloud_user": "Cuenta de iCloud", "cfg_icloud_pass": "Contrasena",
  "deps_title": "Instalar dependencias",
  "deps_q": "Se van a instalar las dependencias de doc/requirements.txt.\n\nRequiere conexion a internet y puede tardar un rato.\n\n Continuar?",
  "missing": "Faltan estas dependencias", "allok": "Todas las dependencias estan instaladas.",
  "ph_db": "msgstore.db (Android)  /  ChatStorage.sqlite (iOS)",
  "ph_wa": "wa.db (Android)  /  ContactsV2.sqlite (iOS)  -  da los nombres",
  "ph_ct": "Contatos.txt  -  display_name=Nombre, data1=numero",
  "ph_enc": "msgstore.db.crypt15  /  .crypt14  /  .crypt12",
  "ph_key": "archivo key  /  encrypted_backup.key  /  64 caracteres hex",
  "ph_out": "carpeta donde se guardara el informe",
  "ph_outfile": "msgstore.db  (archivo que se generara)",
  "ph_media": "carpeta WhatsApp copiada del telefono (la que contiene Media)",
  "ph_chat": "Chat de WhatsApp con <nombre>.txt",
  "ph_chatmedia": "por defecto, la misma carpeta que el .txt",
  "ph_mergedir": "carpeta con varios msgstore.db",
  "ph_mergeout": "msgstore_merge.db  (archivo que se generara)",
  "ph_cipher_in": "Base cifrada o descifrada", "ph_keyfile": "Archivo de clave",
  "ph_cipher_out": "Archivo o carpeta de salida", "ph_merge_folder": "Carpeta con msgstore*.db",
  "ph_content": "contenido, archivo o cita", "ph_sender_hint": "numero o nombre",
  "ph_user_shown": "nombre tal y como aparece", "ph_remote": "ruta remota",
  "ph_chat_export": "Chat exportado (.txt)", "all_files": "Todos",
  "plat_android": "Android actual", "plat_android_legacy": "Android antiguo",
  "f_case": "May/min", "f_word": "Palabra completa", "f_web": "WhatsApp Web",
  "f_starred": "Destacados", "f_forwarded": "Reenviados", "f_edited": "Editados",
  "f_media": "Con adjunto", "f_location": "Con coordenadas",
  "f_read": "Leidos", "f_unread": "Sin confirmar lectura",
  "ty_text": "Texto", "ty_image": "Imagen", "ty_audio": "Audio", "ty_video": "Video",
  "ty_contact": "Contacto", "ty_loc": "Ubicacion", "ty_call": "Llamada",
  "ty_doc": "Documento", "ty_gif": "GIF", "ty_deleted": "Borrado",
  "ty_live": "Ubic. tiempo real", "ty_sticker": "Sticker", "ty_sys": "Sistema",
  "ty_poll": "Encuesta", "ty_viewonce": "Vision unica", "ty_note": "Nota de video",
  "ty_event": "Evento",
  "ph_case": "Diligencias 1234/2026  -  saldra en la portada",
  "ph_examiner": "quien firma el analisis",
  "warn_data": "Faltan datos", "warn_db": "Elige una base de datos.",
  "warn_in": "Entrada, clave y salida son obligatorias.",
  "warn_folder": "Elige la carpeta con las bases.", "warn_chat": "Elige el archivo del chat.",
  "warn_remote": "Indica el archivo a descargar.", "warn_file": "Indica el archivo.",
  "not_found": "No se encuentra {}", "ft_text": "Texto", "ft_db": "Bases",
  "ic_pull": "Descargar un archivo",
  "fin_ok": "Proceso terminado correctamente.",
  "fin_code": "Proceso terminado con codigo {}.",
  "err_exec": "No se pudo ejecutar: {}",
  "license": "Licencia GPL-3.0",
  "import_ctk": "Falta customtkinter. Instalalo con: pip install customtkinter",
  "warn_wrong_db_wa": "Parece wa.db (contactos), no msgstore.db (mensajes).\n\nUsa msgstore.db descifrado en Base de datos.\nwa.db va solo en Contactos (opcional).",
  "warn_wrong_db": "Base de datos no reconocida.\n\nWhaPa analiza:\n- Android: msgstore.db (descifrado)\n- iOS: ChatStorage.sqlite\n\nwa.db solo sirve para nombres de contactos.",
 },
 "EN": {
  "subtitle": "WhatsApp forensics - Android and iOS",
  "output": "Output", "clear": "Clear", "browse": "Browse",
  "deps": "Install requirements", "settings": "Settings",
  "readme": "Manual", "about": "About", "lang": "Espanol",
  "run": "Run", "hint_start": "Pick a tab, fill in the fields and press the action button.",
  "db": "Database", "db_dec": "Decrypted database", "contacts": "Contacts (optional)",
  "contacts_txt": "Phone address book (txt)",
  "outdir": "Output folder", "wafolder": "WhatsApp folder (optional)",
  "copymedia": "Copy attachments into the report (single deliverable package)",
  "mode": "Mode", "platform": "Platform", "auto": "Autodetect",
  "m_msg": "Messages", "m_status": "Info: status", "m_calls": "Info: calls",
  "m_chats": "Info: active chats", "m_extract": "Extract attachments", "m_carving": "Carving",
  "recipients": "Recipients", "scope": "Scope", "all": "All", "user": "User",
  "group": "Group", "byuser": "Messages from a number", "broadcast": "Broadcast",
  "target": "Number or group", "filters": "Filters", "text": "Text",
  "sender": "Sender", "from": "From", "to": "To", "rawtypes": "Native type codes",
  "direction": "Direction", "d_all": "All", "d_sent": "Sent",
  "d_recv": "Received", "d_sys": "System",
  "searchopts": "SEARCH OPTIONS", "types": "MESSAGE TYPES (leave all unticked to include every type)",
  "outsec": "Output", "report": "Interactive report", "none": "None",
  "print": "Printable report", "csv": "Export CSV", "kml": "Export locations to KML",
  "maps": "Download maps (needs internet)", "single": "Single file report",
  "pack": "Export selected chat (tar.gz)",
  "warn_pack": "To pack a single chat set Scope = User or Group and enter the number.",
  "cipher_sec": "Database decryption and encryption", "action": "Action",
  "decrypt": "Decrypt", "encrypt": "Encrypt (crypt15)", "input": "Input file",
  "isdir": "Input is a folder (decryption only)", "key": "Key",
  "keyhint": "The key can be the .key file, encrypted_backup.key, or the 64 hex characters of the root key.",
  "outfile": "Output", "merge_sec": "Database merge",
  "mergefolder": "Folder with the databases", "mergeout": "Resulting database",
  "gd_sec": "Google Drive", "gd_cred": "Credentials are read from cfg/settings.cfg, section [google-auth].",
  "gd_info": "Backup information", "gd_list": "List everything", "gd_listwa": "List WhatsApp backups",
  "gd_pull": "Download a file", "gd_sync": "Sync everything", "gd_img": "Images only",
  "gd_vid": "Videos only", "gd_aud": "Audio only", "gd_doc": "Documents only", "gd_db": "Databases only",
  "remotefile": "File to download", "threads": "Threads",
  "noparallel": "No parallel downloads", "dryrun": "Dry run (no download)",
  "chat_sec": "Chat exported from the app", "chatfile": "Chat file",
  "system": "System", "chatuser": "Target user", "datemask": "Date mask",
  "onlypart": "List participants only", "ic_sec": "iCloud",
  "chatmedia": "Folder with the exported attachments",
  "copymedia_short": "Copy attachments into report", "regex": "Regex",
  "ic_cred": "Credentials are read from cfg/settings.cfg, section [icloud-auth].",
  "ic_list": "List", "ic_sync": "Sync everything", "ic_img": "Images only",
  "ic_vid": "Videos and audio only",
  "cfg_title": "Settings", "cfg_report": "Report details",
  "cfg_google": "Google Drive", "cfg_icloud": "iCloud", "cfg_save": "Save",
  "cfg_cancel": "Cancel", "cfg_saved": "Settings saved to cfg/settings.cfg",
  "cfg_company": "Company / Agency", "cfg_record": "Case / record reference",
  "cfg_unit": "Unit", "cfg_examiner": "Examiner / analyst", "cfg_notes": "Notes",
  "cfg_gmail": "Gmail account", "cfg_password": "Password (or app password if using 2FA)",
  "cfg_oauth": "OAuth cookie (optional)", "cfg_android_id": "android_id",
  "cfg_celnumbr": "Numbers to sync (optional)",
  "cfg_icloud_user": "iCloud account", "cfg_icloud_pass": "Password",
  "deps_title": "Install requirements",
  "deps_q": "This will install everything in doc/requirements.txt.\n\nIt needs an internet connection and may take a while.\n\nContinue?",
  "missing": "These requirements are missing", "allok": "All requirements are installed.",
  "ph_db": "msgstore.db (Android)  /  ChatStorage.sqlite (iOS)",
  "ph_wa": "wa.db (Android)  /  ContactsV2.sqlite (iOS)  -  adds the names",
  "ph_ct": "Contatos.txt  -  display_name=Name, data1=number",
  "ph_enc": "msgstore.db.crypt15  /  .crypt14  /  .crypt12",
  "ph_key": "key file  /  encrypted_backup.key  /  64 hex characters",
  "ph_out": "folder where the report will be written",
  "ph_outfile": "msgstore.db  (file to be created)",
  "ph_media": "WhatsApp folder copied from the phone (the one holding Media)",
  "ph_chat": "WhatsApp Chat with <name>.txt",
  "ph_chatmedia": "defaults to the same folder as the .txt",
  "ph_mergedir": "folder holding several msgstore.db",
  "ph_mergeout": "msgstore_merge.db  (file to be created)",
  "ph_cipher_in": "Encrypted or decrypted database", "ph_keyfile": "Key file",
  "ph_cipher_out": "Output file or folder", "ph_merge_folder": "Folder with msgstore*.db",
  "ph_content": "content, file or quote", "ph_sender_hint": "number or name",
  "ph_user_shown": "name exactly as shown", "ph_remote": "remote path",
  "ph_chat_export": "Exported chat (.txt)", "all_files": "All",
  "plat_android": "Current Android", "plat_android_legacy": "Legacy Android",
  "f_case": "Case sensitive", "f_word": "Whole word", "f_web": "WhatsApp Web",
  "f_starred": "Starred", "f_forwarded": "Forwarded", "f_edited": "Edited",
  "f_media": "With attachment", "f_location": "With coordinates",
  "f_read": "Read", "f_unread": "No read receipt",
  "ty_text": "Text", "ty_image": "Image", "ty_audio": "Audio", "ty_video": "Video",
  "ty_contact": "Contact", "ty_loc": "Location", "ty_call": "Call",
  "ty_doc": "Document", "ty_gif": "GIF", "ty_deleted": "Deleted",
  "ty_live": "Live location", "ty_sticker": "Sticker", "ty_sys": "System",
  "ty_poll": "Poll", "ty_viewonce": "View once", "ty_note": "Video note",
  "ty_event": "Event",
  "ph_case": "Case 1234/2026  -  printed on the cover",
  "ph_examiner": "who signs the analysis",
  "warn_data": "Missing data", "warn_db": "Choose a database.",
  "warn_in": "Input, key and output are required.",
  "warn_folder": "Choose the folder with the databases.", "warn_chat": "Choose the chat file.",
  "warn_remote": "Enter the file to download.", "warn_file": "Enter the file.",
  "not_found": "Not found {}", "ft_text": "Text", "ft_db": "Databases",
  "ic_pull": "Download a file",
  "fin_ok": "Process finished successfully.",
  "fin_code": "Process finished with exit code {}.",
  "err_exec": "Could not run: {}",
  "license": "GPL-3.0 License",
  "import_ctk": "customtkinter is missing. Install it with: pip install customtkinter",
  "warn_wrong_db_wa": "This looks like wa.db (contacts), not msgstore.db (messages).\n\nUse decrypted msgstore.db in Database.\nwa.db belongs in Contacts (optional) only.",
  "warn_wrong_db": "Unrecognized database.\n\nWhaPa expects:\n- Android: msgstore.db (decrypted)\n- iOS: ChatStorage.sqlite\n\nwa.db is only for contact names.",
 },
}

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("green")

F11 = dict(size=11)
F12 = dict(size=12)


def tool(name):
    return os.path.join(LIBS, name)


# Las herramientas se lanzan desde la raiz del proyecto, no desde libs/: si no,
# un informe sin ruta de salida acabaria dentro de libs/, que no es sitio.
# Los modulos de libs/ se importan igual porque cada herramienta anade su propio
# directorio a sys.path.


class Field:
    """Campo de texto con pista visible.

    CustomTkinter solo muestra el placeholder si el campo NO tiene textvariable
    (ver CTkEntry._activate_placeholder). Como aqui interesa mas que el usuario
    vea que archivo se espera, se prescinde de la variable de Tk y se habla
    directamente con el widget, manteniendo la misma interfaz .get() / .set()
    para que el resto del codigo no cambie.
    """

    def __init__(self, value=""):
        self._widget = None
        self._value = value

    def attach(self, widget):
        self._widget = widget
        if self._value:
            widget.insert(0, self._value)

    def get(self):
        if self._widget is not None:
            try:
                return self._widget.get()
            except Exception:
                pass
        return self._value

    def set(self, valor):
        self._value = valor or ""
        if self._widget is None:
            return
        try:
            self._widget.delete(0, "end")
            if valor:
                self._widget.insert(0, valor)
            else:
                # al vaciarlo, la pista debe volver a verse
                self._widget._activate_placeholder()
        except Exception:
            pass


class Row:
    """Ayudante para colocar controles en rejilla dentro de un marco."""

    def __init__(self, master, T=None):
        self.m = master
        self.T = T or (lambda k: k)
        self.r = 0
        self.m.grid_columnconfigure(1, weight=1)
        self.m.grid_columnconfigure(2, weight=0)

    def file(self, label, var, title, types=None, save=False, folder=False,
             hint=None):
        """hint aparece dentro del campo mientras esta vacio, para que se vea
        que archivo se espera sin tener que abrir el dialogo."""
        ctk.CTkLabel(self.m, text=label, text_color=TEXT, anchor="w",
                     font=ctk.CTkFont(**F12)).grid(row=self.r, column=0, sticky="w",
                                                   padx=(12, 6), pady=4)
        e = ctk.CTkEntry(self.m, fg_color=FIELD, border_width=0,
                         placeholder_text=hint or "")
        e.grid(row=self.r, column=1, sticky="ew", pady=4, padx=(0, 6))
        var.attach(e)

        def pick():
            if folder:
                p = filedialog.askdirectory(title=title)
            elif save:
                p = filedialog.asksaveasfilename(title=title, filetypes=types or [(self.T("all_files"), "*.*")])
            else:
                p = filedialog.askopenfilename(title=title, filetypes=types or [(self.T("all_files"), "*.*")])
            if p:
                var.set(p)

        ctk.CTkButton(self.m, text=self.T("browse"), width=86, command=pick,
                      fg_color=FIELD, hover_color="#2a3942", font=ctk.CTkFont(**F11)
                      ).grid(row=self.r, column=2, padx=(0, 12), pady=4)
        self.r += 1

    def entry(self, label, var, placeholder="", width=200):
        ctk.CTkLabel(self.m, text=label, text_color=TEXT, anchor="w",
                     font=ctk.CTkFont(**F12)).grid(row=self.r, column=0, sticky="w",
                                                   padx=(12, 6), pady=4)
        e = ctk.CTkEntry(self.m, fg_color=FIELD, border_width=0,
                         placeholder_text=placeholder, width=width)
        e.grid(row=self.r, column=1, sticky="w", pady=4)
        var.attach(e)
        self.r += 1

    def options(self, label, var, values, width=190):
        ctk.CTkLabel(self.m, text=label, text_color=TEXT, anchor="w",
                     font=ctk.CTkFont(**F12)).grid(row=self.r, column=0, sticky="w",
                                                   padx=(12, 6), pady=4)
        ctk.CTkOptionMenu(self.m, variable=var, values=values, width=width,
                          fg_color=FIELD, button_color=FIELD,
                          button_hover_color="#2a3942", font=ctk.CTkFont(**F12)
                          ).grid(row=self.r, column=1, sticky="w", pady=4)
        self.r += 1

    def checks(self, items, cols=5, label=None):
        """items: lista de (variable, texto)."""
        if label:
            ctk.CTkLabel(self.m, text=label, text_color=MUTED, anchor="w",
                         font=ctk.CTkFont(size=10)).grid(row=self.r, column=0,
                                                         columnspan=4, sticky="w",
                                                         padx=12, pady=(8, 0))
            self.r += 1
        box = ctk.CTkFrame(self.m, fg_color="transparent")
        box.grid(row=self.r, column=0, columnspan=4, sticky="w", padx=10, pady=2)
        for i, (var, txt) in enumerate(items):
            ctk.CTkCheckBox(box, text=txt, variable=var, text_color=TEXT,
                            fg_color=ACCENT, hover_color=ACCENT_HOVER,
                            checkbox_width=16, checkbox_height=16,
                            font=ctk.CTkFont(size=11)
                            ).grid(row=i // cols, column=i % cols, sticky="w",
                                   padx=6, pady=2)
        self.r += 1

    def section(self, text):
        ctk.CTkLabel(self.m, text=text, text_color=ACCENT,
                     font=ctk.CTkFont(size=12, weight="bold")
                     ).grid(row=self.r, column=0, columnspan=4, sticky="w",
                            padx=12, pady=(10, 2))
        self.r += 1

    def run(self, text, command):
        b = ctk.CTkButton(self.m, text=text, command=command, width=180,
                          fg_color=ACCENT, hover_color=ACCENT_HOVER,
                          text_color="#04160f",
                          font=ctk.CTkFont(size=13, weight="bold"))
        b.grid(row=self.r, column=0, columnspan=2, sticky="w", padx=12, pady=12)
        self.r += 1
        return b


class SettingsDialog(ctk.CTkToplevel):
    """Editor de cfg/settings.cfg: datos del informe y credenciales."""

    CAMPOS = [
        ("report", "company",   "cfg_company"),
        ("report", "record",    "cfg_record"),
        ("report", "unit",      "cfg_unit"),
        ("report", "examiner",  "cfg_examiner"),
        ("report", "notes",     "cfg_notes"),
        ("google-auth", "gmail",      "cfg_gmail"),
        ("google-auth", "password",   "cfg_password"),
        ("google-auth", "oauth",      "cfg_oauth"),
        ("google-auth", "android_id", "cfg_android_id"),
        ("google-auth", "celnumbr",   "cfg_celnumbr"),
        ("icloud-auth", "icloud", "cfg_icloud_user"),
        ("icloud-auth", "passw",  "cfg_icloud_pass"),
    ]
    SECCIONES = {"report": "cfg_report", "google-auth": "cfg_google",
                 "icloud-auth": "cfg_icloud"}

    def __init__(self, master):
        super().__init__(master)
        self.master_gui = master
        self.title(master.T("cfg_title"))
        self.geometry("640x620")
        self.configure(fg_color=BG)
        self.transient(master)
        self.ruta = os.path.join(APP_DIR, "cfg", "settings.cfg")
        self.vars = {}
        self._build()
        self.after(120, self.grab_set)     # tras dibujarse, para no fallar en Linux

    def _build(self):
        T = self.master_gui.T
        sc = ctk.CTkScrollableFrame(self, fg_color="transparent")
        sc.pack(fill="both", expand=True, padx=12, pady=12)
        sc.grid_columnconfigure(1, weight=1)

        cfg = ConfigParser()
        if os.path.exists(self.ruta):
            try:
                cfg.read(self.ruta, encoding="utf-8")
            except Exception:
                pass

        fila = 0
        seccion_actual = None
        for sec, clave, etiqueta in self.CAMPOS:
            if sec != seccion_actual:
                seccion_actual = sec
                ctk.CTkLabel(sc, text=T(self.SECCIONES[sec]), text_color=ACCENT,
                             font=ctk.CTkFont(size=13, weight="bold")
                             ).grid(row=fila, column=0, columnspan=2, sticky="w",
                                    pady=(14, 4))
                fila += 1
            valor = ""
            if cfg.has_option(sec, clave):
                valor = cfg.get(sec, clave).strip().strip('"')
            var = ctk.StringVar(value=valor)
            self.vars[(sec, clave)] = var
            ctk.CTkLabel(sc, text=T(etiqueta), text_color=TEXT, anchor="w",
                         font=ctk.CTkFont(**F12)).grid(row=fila, column=0,
                                                       sticky="w", padx=(0, 10), pady=3)
            oculta = "*" if clave in ("password", "passw") else ""
            placeholder = ""
            if sec == "report" and clave == "record":
                placeholder = T("ph_case")
            elif sec == "report" and clave == "examiner":
                placeholder = T("ph_examiner")
            ctk.CTkEntry(sc, textvariable=var, fg_color=FIELD, border_width=0,
                         show=oculta, width=330,
                         placeholder_text=placeholder).grid(row=fila, column=1,
                                                      sticky="ew", pady=3)
            fila += 1

        barra = ctk.CTkFrame(self, fg_color="transparent")
        barra.pack(fill="x", padx=12, pady=(0, 12))
        ctk.CTkButton(barra, text=T("cfg_save"), command=self._save, width=130,
                      fg_color=ACCENT, hover_color=ACCENT_HOVER,
                      text_color="#04160f",
                      font=ctk.CTkFont(size=13, weight="bold")).pack(side="right")
        ctk.CTkButton(barra, text=T("cfg_cancel"), command=self.destroy, width=110,
                      fg_color=FIELD, hover_color="#2a3942").pack(side="right", padx=8)
        ctk.CTkLabel(barra, text=self.ruta, text_color=MUTED,
                     font=ctk.CTkFont(size=10)).pack(side="left")

    def _save(self):
        cfg = ConfigParser()
        if os.path.exists(self.ruta):
            try:
                cfg.read(self.ruta, encoding="utf-8")
            except Exception:
                pass
        for (sec, clave), var in self.vars.items():
            if not cfg.has_section(sec):
                cfg.add_section(sec)
            valor = var.get()
            # los datos del informe se guardan entrecomillados, como en el original
            if sec == "report":
                valor = '"{}"'.format(valor.replace('"', ""))
            cfg.set(sec, clave, valor)
        try:
            os.makedirs(os.path.dirname(self.ruta), exist_ok=True)
            with open(self.ruta, "w", encoding="utf-8") as fh:
                cfg.write(fh)
            self.master_gui._emit("[-] " + self.master_gui.T("cfg_saved"), "ok")
            self.destroy()
        except OSError as e:
            messagebox.showerror("whapa", str(e))


class WhapaGUI(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("WhaPa {} - Whatsapp Parser".format(version))
        # El tamano inicial nunca debe superar la pantalla: en un equipo de
        # 1024x768 una ventana de 1060x860 se sale y no se ven los botones.
        try:
            _sw, _sh = self.winfo_screenwidth(), self.winfo_screenheight()
        except Exception:
            _sw, _sh = 1280, 800
        self.geometry("{}x{}".format(min(1060, _sw - 20), min(860, _sh - 80)))
        self.minsize(min(900, _sw - 40), min(640, _sh - 100))
        self.configure(fg_color=BG)
        self.q = queue.Queue()
        self.busy = False
        self.buttons = []
        self.lang = "IT"
        self._set_icon()
        self._build()
        # Se maximiza cuando la ventana ya existe: hacerlo dentro de __init__,
        # antes de que el gestor de ventanas la dibuje, no surte efecto.
        self.after(10, self._maximizar)
        self.after(100, self._drain)

    def _maximizar(self):
        """Abre la ventana maximizada, con el metodo que admita cada sistema.

        No hay uno que valga para todos: Windows entiende state("zoomed"),
        varios gestores de ventanas de Linux usan el atributo -zoomed, y en
        macOS no funciona ninguno, asi que se recurre a ajustar la geometria al
        tamano de la pantalla. Se prueban en ese orden y se comprueba el
        resultado, porque un metodo puede no dar error y aun asi no hacer nada.
        """
        try:
            pantalla_ancho = self.winfo_screenwidth()
            pantalla_alto = self.winfo_screenheight()
        except Exception:
            return

        def maximizada():
            try:
                return (self.winfo_width() >= pantalla_ancho * 0.92
                        and self.winfo_height() >= pantalla_alto * 0.80)
            except Exception:
                return False

        for metodo in (lambda: self.state("zoomed"),
                       lambda: self.attributes("-zoomed", True)):
            try:
                metodo()
                self.update_idletasks()
                if maximizada():
                    return
            except Exception:
                continue

        # Ultimo recurso: ocupar la pantalla a mano, dejando hueco para la
        # barra de tareas.
        try:
            self.geometry("{}x{}+0+0".format(pantalla_ancho,
                                             max(500, pantalla_alto - 70)))
        except Exception:
            pass

    # ------------------------------------------------------------------
    def T(self, clave):
        """Texto en el idioma activo."""
        return LANG[self.lang].get(clave, clave)

    def _optmap(self, *keys):
        """Mappa etichette tradotte -> chiavi interne (stabile per i menu)."""
        return {self.T(k): k for k in keys}

    def _db_tables(self, path):
        import sqlite3
        con = sqlite3.connect(path)
        try:
            return {r[0] for r in con.execute(
                "SELECT name FROM sqlite_master WHERE type='table'")}
        finally:
            con.close()

    def _validate_db(self, path):
        """Avvisa se l'utente ha scelto wa.db al posto di msgstore.db."""
        try:
            tables = self._db_tables(path)
        except Exception:
            return True
        if "message" in tables or "messages" in tables or "ZWAMESSAGE" in tables:
            return True
        if "wa_contacts" in tables or (
                "dismissed_chat" in tables and "message" not in tables):
            messagebox.showwarning(self.T("warn_data"), self.T("warn_wrong_db_wa"))
            return False
        messagebox.showwarning(self.T("warn_data"), self.T("warn_wrong_db"))
        return False

    def _set_icon(self):
        """Icono de la ventana, desde images/."""
        ico = os.path.join(APP_DIR, "images", "logo.ico")
        png = os.path.join(APP_DIR, "images", "logo.png")
        try:
            if sys.platform.startswith("win") and os.path.exists(ico):
                self.iconbitmap(ico)
            elif os.path.exists(png):
                import tkinter as tk
                self._icon_img = tk.PhotoImage(file=png)
                self.iconphoto(True, self._icon_img)
        except Exception:
            pass          # el icono es un detalle: nunca debe impedir arrancar

    def _switch_lang(self):
        self.lang = {"IT": "EN", "EN": "ES", "ES": "IT"}[self.lang]
        registro = self.log.get("1.0", "end")
        for w in self.winfo_children():
            w.destroy()
        self.buttons = []
        self._build()
        if registro.strip():
            self.log.insert("end", registro)

    # ------------------------------------------------------------------
    def _build(self):
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)
        self.grid_rowconfigure(2, minsize=210)

        head = ctk.CTkFrame(self, fg_color="transparent")
        head.grid(row=0, column=0, sticky="ew", padx=14, pady=(12, 4))
        ctk.CTkLabel(head, text="WhaPa", text_color=ACCENT,
                     font=ctk.CTkFont(size=22, weight="bold")).pack(side="left")
        ctk.CTkLabel(head, text="   " + self.T("subtitle"),
                     text_color=MUTED, font=ctk.CTkFont(**F12)).pack(side="left")

        # barra de herramientas
        for txt, cmd in ((self.T("lang"), self._switch_lang),
                         (self.T("about"), self._about),
                         (self.T("readme"), self._readme),
                         (self.T("settings"), self._settings),
                         (self.T("deps"), self._install_deps)):
            ctk.CTkButton(head, text=txt, command=cmd, width=136,
                          fg_color=FIELD, hover_color="#2a3942",
                          font=ctk.CTkFont(**F11)).pack(side="right", padx=3)

        self.tabs = ctk.CTkTabview(self, fg_color=PANEL, segmented_button_fg_color=FIELD,
                                   segmented_button_selected_color=ACCENT,
                                   segmented_button_selected_hover_color=ACCENT_HOVER)
        self.tabs.grid(row=1, column=0, sticky="nsew", padx=14, pady=4)
        for name in ("WhaPa", "WhaCipher", "WhaMerge", "WhaGoDri", "WhaChat", "WhaCloud"):
            self.tabs.add(name)

        self._tab_whapa(self.tabs.tab("WhaPa"))
        self._tab_whacipher(self.tabs.tab("WhaCipher"))
        self._tab_whamerge(self.tabs.tab("WhaMerge"))
        self._tab_whagodri(self.tabs.tab("WhaGoDri"))
        self._tab_whachat(self.tabs.tab("WhaChat"))
        self._tab_whacloud(self.tabs.tab("WhaCloud"))

        bottom = ctk.CTkFrame(self, fg_color="transparent")
        bottom.grid(row=2, column=0, sticky="nsew", padx=14, pady=(4, 12))
        bottom.grid_columnconfigure(0, weight=1)
        bottom.grid_rowconfigure(1, weight=1)

        bar = ctk.CTkFrame(bottom, fg_color="transparent")
        bar.grid(row=0, column=0, sticky="ew")
        ctk.CTkLabel(bar, text=self.T("output"), text_color=ACCENT,
                     font=ctk.CTkFont(size=12, weight="bold")).pack(side="left")
        ctk.CTkButton(bar, text=self.T("clear"), width=80, command=self._clear,
                      fg_color=FIELD, hover_color="#2a3942",
                      font=ctk.CTkFont(**F11)).pack(side="right", padx=4)
        self.progress = ctk.CTkProgressBar(bar, width=160, mode="indeterminate",
                                           progress_color=ACCENT)
        self.progress.pack(side="right", padx=8)
        self.progress.set(0)

        self.log = ctk.CTkTextbox(bottom, fg_color=PANEL, text_color=TEXT,
                                  corner_radius=10, wrap="word",
                                  font=ctk.CTkFont(family="Consolas", size=12))
        self.log.grid(row=1, column=0, sticky="nsew", pady=(4, 0))
        self.log.tag_config("ok", foreground=ACCENT)
        self.log.tag_config("err", foreground=ERROR)
        self.log.tag_config("cmd", foreground=MUTED)
        self._emit(self.T("hint_start"), "cmd")


    # ------------------------------------------------------------------
    #  Barra de herramientas
    # ------------------------------------------------------------------
    def _install_deps(self):
        """Instala doc/requirements.txt con el pip del interprete en uso."""
        req = os.path.join(APP_DIR, "doc", "requirements.txt")
        if not os.path.exists(req):
            return messagebox.showerror("whapa", self.T("not_found").format(req))
        faltan = []
        try:
            sys.path.insert(0, LIBS)
            import whadeps
            faltan = whadeps.check("Crypto", "colorama", "customtkinter", "requests",
                                   "pandas", "numpy", "configobj", "click",
                                   "pyicloud", "selenium", "Cryptodome")
        except Exception:
            pass
        detalle = ("\n\n{}: {}".format(self.T("missing"), ", ".join(faltan))
                   if faltan else "\n\n" + self.T("allok"))
        if not messagebox.askyesno(self.T("deps_title"),
                                   self.T("deps_q") + detalle):
            return
        # se usa el pip del interprete que esta ejecutando la interfaz, para no
        # instalar en un Python distinto del que luego ejecuta las herramientas
        self._launch_raw([sys.executable, "-m", "pip", "install", "--upgrade",
                          "-r", req])

    def _settings(self):
        """Editor de cfg/settings.cfg."""
        SettingsDialog(self)

    def _readme(self):
        ruta = os.path.join(APP_DIR, "README.md")
        if os.path.exists(ruta):
            webbrowser.open("file://" + os.path.abspath(ruta))
        else:
            webbrowser.open("https://github.com/B16f00t/whapa")

    def _about(self):
        messagebox.showinfo(
            "WhaPa " + version,
            "WhaPa {} - Whatsapp Parser Toolset\n\n"
            "Android e iOS\n"
            "Ivan Moreno (B16f00t)\n"
            "https://github.com/B16f00t/whapa\n\n"
            "{}".format(version, self.T("license")))

    # ---------------- pestana WhaPa ----------------
    def _tab_whapa(self, tab):
        sc = ctk.CTkScrollableFrame(tab, fg_color="transparent")
        sc.pack(fill="both", expand=True)
        r = Row(sc, self.T)
        self.p_db, self.p_wa, self.p_ct, self.p_out = Field(), Field(), Field(), Field()
        r.section(self.T("db"))
        r.file(self.T("db_dec"), self.p_db, "msgstore.db / ChatStorage.sqlite",
               [("SQLite", "*.db *.sqlite"), (self.T("all_files"), "*.*")],
               hint=self.T("ph_db"))
        r.file(self.T("contacts"), self.p_wa, "wa.db / ContactsV2.sqlite",
               [("SQLite", "*.db *.sqlite"), (self.T("all_files"), "*.*")],
               hint=self.T("ph_wa"))
        r.file(self.T("contacts_txt"), self.p_ct, "Contatos.txt",
               [(self.T("ft_text"), "*.txt"), (self.T("all_files"), "*.*")],
               hint=self.T("ph_ct"))
        r.file(self.T("outdir"), self.p_out, self.T("outdir"), folder=True,
               hint=self.T("ph_out"))
        self.p_media = Field()
        r.file(self.T("wafolder"), self.p_media, self.T("wafolder"), folder=True,
               hint=self.T("ph_media"))
        self.p_copymedia = ctk.BooleanVar()
        r.checks([(self.p_copymedia,
                   self.T("copymedia"))],
                 cols=1)

        r.section(self.T("mode"))
        self.p_mode = ctk.StringVar(value=self.T("m_msg"))
        r.options(self.T("mode"), self.p_mode,
                  [self.T("m_msg"), self.T("m_status"), self.T("m_calls"),
                   self.T("m_chats"), self.T("m_extract"), self.T("m_carving")])
        self.p_platform = ctk.StringVar(value=self.T("auto"))
        r.options(self.T("platform"), self.p_platform,
                  [self.T("auto"), self.T("plat_android"),
                   self.T("plat_android_legacy"), "iOS"])

        r.section(self.T("recipients"))
        self.p_recip = ctk.StringVar(value=self.T("all"))
        r.options(self.T("scope"), self.p_recip,
                  [self.T("all"), self.T("user"), self.T("group"),
                   self.T("byuser"), self.T("broadcast")])
        self.p_target = Field()
        r.entry(self.T("target"), self.p_target, "34123456789  /  1234-5678@g.us", 260)

        r.section(self.T("filters"))
        self.p_text, self.p_sender = Field(), Field()
        self.p_ts, self.p_te, self.p_raw = Field(), Field(), Field()
        r.entry(self.T("text"), self.p_text, self.T("ph_content"), 280)
        r.entry(self.T("sender"), self.p_sender, self.T("ph_sender_hint"), 200)
        r.entry(self.T("from"), self.p_ts, "dd-mm-aaaa HH:MM", 180)
        r.entry(self.T("to"), self.p_te, "dd-mm-aaaa HH:MM", 180)
        r.entry(self.T("rawtypes"), self.p_raw, "66,112", 140)
        self.p_dir = ctk.StringVar(value=self.T("d_all"))
        r.options(self.T("direction"), self.p_dir,
                  [self.T("d_all"), self.T("d_sent"), self.T("d_recv"), self.T("d_sys")])

        self.p_flags = {}
        for k in ("regex", "case", "word", "web", "starred", "forwarded",
                  "edited", "media", "location", "read", "unread"):
            self.p_flags[k] = ctk.BooleanVar()
        r.checks([(self.p_flags["regex"], self.T("regex")),
                  (self.p_flags["case"], self.T("f_case")),
                  (self.p_flags["word"], self.T("f_word")),
                  (self.p_flags["web"], self.T("f_web")),
                  (self.p_flags["starred"], self.T("f_starred")),
                  (self.p_flags["forwarded"], self.T("f_forwarded")),
                  (self.p_flags["edited"], self.T("f_edited")),
                  (self.p_flags["media"], self.T("f_media")),
                  (self.p_flags["location"], self.T("f_location")),
                  (self.p_flags["read"], self.T("f_read")),
                  (self.p_flags["unread"], self.T("f_unread"))],
                 cols=5, label=self.T("searchopts"))

        self.p_types = {}
        tipos = [("tt", "ty_text"), ("ti", "ty_image"), ("ta", "ty_audio"), ("tv", "ty_video"),
                 ("tc", "ty_contact"), ("tl", "ty_loc"), ("tx", "ty_call"),
                 ("tp", "ty_doc"), ("tg", "ty_gif"), ("td", "ty_deleted"),
                 ("tr", "ty_live"), ("tk", "ty_sticker"), ("tm", "ty_sys"),
                 ("tn", "ty_poll"), ("tq", "ty_viewonce"), ("tj", "ty_note"),
                 ("tz", "ty_event")]
        for k, _ in tipos:
            self.p_types[k] = ctk.BooleanVar()
        r.checks([(self.p_types[k], self.T(tk)) for k, tk in tipos], cols=6,
                 label=self.T("types"))

        r.section(self.T("output"))
        self.p_report = ctk.StringVar(value=self.T("none"))
        r.options(self.T("report"), self.p_report, [self.T("none"), "ES", "EN", "ITA"])
        self.p_out_flags = {k: ctk.BooleanVar()
                            for k in ("print", "csv", "kml", "maps", "single")}
        r.checks([(self.p_out_flags["print"], self.T("print")),
                  (self.p_out_flags["csv"], self.T("csv")),
                  (self.p_out_flags["kml"], self.T("kml")),
                  (self.p_out_flags["maps"], self.T("maps")),
                  (self.p_out_flags["single"], self.T("single"))], cols=3)
        self.p_pack = ctk.StringVar(value=self.T("none"))
        r.options(self.T("pack"), self.p_pack, [self.T("none"), "HTML", "PDF"])
        self._opt_mode = self._optmap("m_msg", "m_status", "m_calls", "m_chats",
                                      "m_extract", "m_carving")
        self._opt_plat = {self.T("plat_android"): "android",
                          self.T("plat_android_legacy"): "android_legacy",
                          "iOS": "ios"}
        self._opt_recip = self._optmap("all", "user", "group", "byuser", "broadcast")
        self._opt_dir = {self.T("d_sent"): "sent",
                         self.T("d_recv"): "received",
                         self.T("d_sys"): "system"}
        self.buttons.append(r.run(self.T("run")+" WhaPa", self._run_whapa))

    def _run_whapa(self):
        if not self.p_db.get():
            return messagebox.showwarning(self.T("warn_data"), self.T("warn_db"))
        if not self._validate_db(self.p_db.get()):
            return
        a = [tool("whapa.py"), self.p_db.get()]
        mode = self._opt_mode.get(self.p_mode.get(), "m_carving")
        if mode == "m_msg":
            a.append("-m")
        elif mode == "m_status":
            a += ["-i", "1"]
        elif mode == "m_calls":
            a += ["-i", "2"]
        elif mode == "m_chats":
            a += ["-i", "3"]
        elif mode == "m_extract":
            a.append("-e")
        else:
            a.append("-c")

        plat = self._opt_plat.get(self.p_platform.get())
        if plat:
            a += ["--platform", plat]
        if self.p_wa.get():
            a += ["-wa", self.p_wa.get()]
        if self.p_ct.get():
            a += ["--contacts_txt", self.p_ct.get()]
        if self.p_out.get():
            a += ["-o", self.p_out.get()]
        if self.p_media.get():
            a += ["-mp", self.p_media.get()]
            if self.p_copymedia.get():
                a.append("-cm")

        if mode == "m_msg":
            alc = self._opt_recip.get(self.p_recip.get(), "all")
            tgt = self.p_target.get().strip()
            if alc == "all":
                a.append("-a")
            elif alc == "broadcast":
                a += ["-a", "-b"]
            elif alc == "user" and tgt:
                a += ["-u", tgt]
            elif alc == "group" and tgt:
                a += ["-g", tgt]
            elif alc == "byuser" and tgt:
                a += ["-ua", tgt]
            else:
                a.append("-a")

            if self.p_text.get():
                a += ["-t", self.p_text.get()]
            if self.p_sender.get():
                a += ["-sn", self.p_sender.get()]
            if self.p_ts.get():
                a += ["-ts", self.p_ts.get()]
            if self.p_te.get():
                a += ["-te", self.p_te.get()]
            if self.p_raw.get():
                a += ["-rt", self.p_raw.get()]
            d = self._opt_dir.get(self.p_dir.get())
            if d:
                a += ["-d", d]
            for k, flag in (("regex", "-re"), ("case", "-cs"), ("word", "-ww"),
                            ("web", "-w"), ("starred", "-s"), ("forwarded", "-fw"),
                            ("edited", "-ed"), ("media", "-md"), ("location", "-gp"),
                            ("read", "-lr"), ("unread", "-lu")):
                if self.p_flags[k].get():
                    a.append(flag)
            for k, v in self.p_types.items():
                if v.get():
                    a.append("-" + k)
            if self.p_report.get() != self.T("none"):
                a += ["-r", self.p_report.get()]
            if self.p_out_flags["print"].get():
                a.append("-p")
            if self.p_out_flags["csv"].get():
                a.append("-x")
            if self.p_out_flags["kml"].get():
                a.append("-k")
            if self.p_out_flags["maps"].get():
                a.append("-gm")
            if self.p_out_flags["single"].get():
                a.append("-1")
            pk = self.p_pack.get()
            if pk != self.T("none"):
                alc = self._opt_recip.get(self.p_recip.get(), "all")
                if alc not in ("user", "group") or not self.p_target.get().strip():
                    return messagebox.showwarning(self.T("warn_data"), self.T("warn_pack"))
                a += ["-z", pk.lower()]
        self._launch(a)

    # ---------------- pestana WhaCipher ----------------
    def _tab_whacipher(self, tab):
        r = Row(tab, self.T)
        self.c_mode = ctk.StringVar(value=self.T("decrypt"))
        self.c_in, self.c_key, self.c_out = Field(), Field(), Field()
        self.c_isdir = ctk.BooleanVar()
        r.section(self.T("cipher_sec"))
        r.options(self.T("action"), self.c_mode,
                  [self.T("decrypt"), self.T("encrypt")])
        r.file(self.T("input"), self.c_in, self.T("ph_cipher_in"),
               [(self.T("ft_db"), "*.crypt12 *.crypt14 *.crypt15 *.db"),
                (self.T("all_files"), "*.*")],
               hint=self.T("ph_enc"))
        r.checks([(self.c_isdir, self.T("isdir"))], cols=1)
        r.file(self.T("key"), self.c_key, self.T("ph_keyfile"),
               hint=self.T("ph_key"))
        ctk.CTkLabel(tab, text=self.T("keyhint"),
                     text_color=MUTED, font=ctk.CTkFont(size=11), wraplength=820,
                     justify="left").grid(row=r.r, column=0, columnspan=4,
                                          sticky="w", padx=12, pady=(0, 4))
        r.r += 1
        r.file(self.T("output"), self.c_out, self.T("ph_cipher_out"), save=True)
        self._opt_cipher = self._optmap("decrypt", "encrypt")
        self.buttons.append(r.run(self.T("run")+" WhaCipher", self._run_whacipher))

    def _run_whacipher(self):
        if not (self.c_in.get() and self.c_key.get() and self.c_out.get()):
            return messagebox.showwarning(self.T("warn_data"), self.T("warn_in"))
        a = [tool("whacipher.py")]
        a += ["-p" if self.c_isdir.get() else "-f", self.c_in.get()]
        if self._opt_cipher.get(self.c_mode.get(), "decrypt") == "decrypt":
            a += ["-d", self.c_key.get()]
        else:
            a += ["-e", self.c_key.get()]
        a += ["-o", self.c_out.get()]
        self._launch(a)

    # ---------------- pestana WhaMerge ----------------
    def _tab_whamerge(self, tab):
        r = Row(tab, self.T)
        self.m_path, self.m_out = Field(), Field()
        r.section(self.T("merge_sec"))
        r.file(self.T("mergefolder"), self.m_path, self.T("ph_merge_folder"),
               folder=True, hint=self.T("ph_mergedir"))
        r.file(self.T("mergeout"), self.m_out, "msgstore_merge.db", save=True,
               hint=self.T("ph_mergeout"))
        self.buttons.append(r.run(self.T("run")+" WhaMerge", self._run_whamerge))

    def _run_whamerge(self):
        if not self.m_path.get():
            return messagebox.showwarning(self.T("warn_data"), self.T("warn_folder"))
        a = [tool("whamerge.py"), self.m_path.get()]
        if self.m_out.get():
            a += ["-o", self.m_out.get()]
        self._launch(a)

    # ---------------- pestana WhaGoDri ----------------
    def _tab_whagodri(self, tab):
        sc = ctk.CTkScrollableFrame(tab, fg_color="transparent")
        sc.pack(fill="both", expand=True)
        r = Row(sc, self.T)
        r.section(self.T("gd_sec"))
        ctk.CTkLabel(sc, text=self.T("gd_cred"), text_color=MUTED,
                     font=ctk.CTkFont(size=11)).grid(row=r.r, column=0, columnspan=4,
                                                     sticky="w", padx=12, pady=(0, 6))
        r.r += 1
        self.g_action = ctk.StringVar(value=self.T("gd_info"))
        r.options(self.T("action"), self.g_action,
                  [self.T("gd_info"), self.T("gd_list"), self.T("gd_listwa"),
                   self.T("gd_pull"), self.T("gd_sync"), self.T("gd_img"),
                   self.T("gd_vid"), self.T("gd_aud"), self.T("gd_doc"),
                   self.T("gd_db")], 250)
        self.g_file, self.g_out = Field(), Field()
        r.entry(self.T("remotefile"), self.g_file, self.T("ph_remote"), 260)
        r.file(self.T("outdir"), self.g_out, self.T("outdir"), folder=True,
               hint=self.T("ph_out"))
        self.g_threads = Field("12")
        r.entry(self.T("threads"), self.g_threads, "12", 80)
        self.g_np, self.g_dry = ctk.BooleanVar(), ctk.BooleanVar()
        r.checks([(self.g_np, self.T("noparallel")),
                  (self.g_dry, self.T("dryrun"))], cols=2)
        self._opt_gd = {
            self.T("gd_info"): "-i", self.T("gd_list"): "-l",
            self.T("gd_listwa"): "-lw", self.T("gd_sync"): "-s",
            self.T("gd_img"): "-si", self.T("gd_vid"): "-sv",
            self.T("gd_aud"): "-sa", self.T("gd_doc"): "-sx",
            self.T("gd_db"): "-sd",
        }
        self._gd_pull = self.T("gd_pull")
        self.buttons.append(r.run(self.T("run")+" WhaGoDri", self._run_whagodri))

    def _run_whagodri(self):
        a = [tool("whagodri.py")]
        acc = self.g_action.get()
        if acc == self._gd_pull:
            if not self.g_file.get():
                return messagebox.showwarning(self.T("warn_data"),
                                              self.T("warn_remote"))
            a += ["-p", self.g_file.get()]
        else:
            flag = self._opt_gd.get(acc)
            if not flag:
                return messagebox.showwarning(self.T("warn_data"),
                                              self.T("warn_remote"))
            a.append(flag)
        if self.g_out.get():
            a += ["-o", self.g_out.get()]
        if self.g_np.get():
            a.append("-np")
        if self.g_dry.get():
            a.append("-dr")
        if self.g_threads.get().isdigit():
            a += ["-tc", self.g_threads.get()]
        self._launch(a)

    # ---------------- pestana WhaChat ----------------
    def _tab_whachat(self, tab):
        r = Row(tab, self.T)
        self.h_file, self.h_user = Field(), Field()
        self.h_fmt, self.h_ts, self.h_te = Field(), Field(), Field()
        r.section(self.T("chat_sec"))
        r.file(self.T("chatfile"), self.h_file, self.T("ph_chat_export"),
               [(self.T("ft_text"), "*.txt"), (self.T("all_files"), "*.*")],
               hint=self.T("ph_chat"))
        self.h_sys = ctk.StringVar(value="android")
        r.options(self.T("system"), self.h_sys, ["android", "ios"], 140)
        self.h_report = ctk.StringVar(value=self.T("none"))
        r.options(self.T("report"), self.h_report,
                  [self.T("none"), "ES", "EN", "ITA"], 140)
        r.entry(self.T("chatuser"), self.h_user, self.T("ph_user_shown"), 260)
        r.entry(self.T("datemask"), self.h_fmt, "%d/%m/%y %H:%M:%S", 200)
        r.entry(self.T("from"), self.h_ts, "dd-mm-aaaa HH:MM", 180)
        r.entry(self.T("to"), self.h_te, "dd-mm-aaaa HH:MM", 180)
        self.h_media = Field()
        r.file(self.T("chatmedia"), self.h_media, self.T("chatmedia"),
               folder=True, hint=self.T("ph_chatmedia"))
        self.h_out = Field()
        r.file(self.T("outdir"), self.h_out, self.T("outdir"), folder=True,
               hint=self.T("ph_out"))
        self.h_text = Field()
        r.entry(self.T("text"), self.h_text, "", 240)
        self.h_part = ctk.BooleanVar()
        self.h_flags = {k: ctk.BooleanVar() for k in ("print", "csv", "copy", "regex")}
        r.checks([(self.h_part, self.T("onlypart")),
                  (self.h_flags["print"], self.T("print")),
                  (self.h_flags["csv"], self.T("csv")),
                  (self.h_flags["copy"], self.T("copymedia_short")),
                  (self.h_flags["regex"], self.T("regex"))], cols=3)
        self.buttons.append(r.run(self.T("run")+" WhaChat", self._run_whachat))

    def _run_whachat(self):
        if not self.h_file.get():
            return messagebox.showwarning(self.T("warn_data"), self.T("warn_chat"))
        a = [tool("whachat.py"), self.h_file.get()]
        if self.h_part.get():
            a.append("-p")
        if self.h_user.get():
            a += ["-u", self.h_user.get()]
        a += ["-s", self.h_sys.get()]
        if self.h_report.get() != self.T("none"):
            a += ["-r", self.h_report.get()]
        if self.h_fmt.get():
            a += ["-f", self.h_fmt.get()]
        if self.h_ts.get():
            a += ["-ts", self.h_ts.get()]
        if self.h_te.get():
            a += ["-te", self.h_te.get()]
        if self.h_out.get():
            a += ["-o", self.h_out.get()]
        if self.h_media.get():
            a += ["-mp", self.h_media.get()]
        if self.h_text.get():
            a += ["-t", self.h_text.get()]
        if self.h_flags["regex"].get():
            a.append("-re")
        if self.h_flags["print"].get():
            a.append("-pr")
        if self.h_flags["csv"].get():
            a.append("-x")
        if self.h_flags["copy"].get():
            a.append("-cm")
        self._launch(a)

    # ---------------- pestana WhaCloud ----------------
    def _tab_whacloud(self, tab):
        r = Row(tab, self.T)
        r.section(self.T("ic_sec"))
        ctk.CTkLabel(tab, text=self.T("ic_cred"), text_color=MUTED,
                     font=ctk.CTkFont(size=11)).grid(row=r.r, column=0, columnspan=4,
                                                     sticky="w", padx=12, pady=(0, 6))
        r.r += 1
        self.k_action = ctk.StringVar(value=self.T("ic_list"))
        r.options(self.T("action"), self.k_action,
                  [self.T("ic_list"), self.T("ic_pull"), self.T("ic_sync"),
                   self.T("ic_img"), self.T("ic_vid")], 230)
        self.k_file, self.k_out = Field(), Field()
        r.entry(self.T("remotefile"), self.k_file, self.T("ph_remote"), 260)
        r.file(self.T("outdir"), self.k_out, self.T("outdir"), folder=True,
               hint=self.T("ph_out"))
        self._opt_ic = {
            self.T("ic_list"): "-l", self.T("ic_sync"): "-s",
            self.T("ic_img"): "-si", self.T("ic_vid"): "-sv",
        }
        self._ic_pull = self.T("ic_pull")
        self.buttons.append(r.run(self.T("run")+" WhaCloud", self._run_whacloud))

    def _run_whacloud(self):
        a = [tool("whacloud.py")]
        acc = self.k_action.get()
        if acc == self._ic_pull:
            if not self.k_file.get():
                return messagebox.showwarning(self.T("warn_data"),
                                              self.T("warn_file"))
            a += ["-p", self.k_file.get()]
        else:
            flag = self._opt_ic.get(acc)
            if not flag:
                return messagebox.showwarning(self.T("warn_data"),
                                              self.T("warn_file"))
            a.append(flag)
        if self.k_out.get():
            a += ["-o", self.k_out.get()]
        self._launch(a)

    # ------------------------------------------------------------------
    #  Ejecucion
    # ------------------------------------------------------------------
    def _emit(self, msg, tag=None):
        self.q.put((msg, tag))

    def _clear(self):
        self.log.delete("1.0", "end")

    def _drain(self):
        """Unico punto que toca la interfaz. Corre en el hilo principal."""
        try:
            while True:
                msg, tag = self.q.get_nowait()
                if tag == "__done__":
                    self._set_busy(False)
                    continue
                self.log.insert("end", msg + "\n", tag or ())
                self.log.see("end")
        except queue.Empty:
            pass
        self.after(120, self._drain)

    def _set_busy(self, busy):
        self.busy = busy
        for b in self.buttons:
            b.configure(state="disabled" if busy else "normal")
        if busy:
            self.progress.start()
        else:
            self.progress.stop()
            self.progress.set(0)

    def _launch_raw(self, argv):
        """Ejecuta una orden completa (ya incluye el interprete)."""
        if self.busy:
            return
        self._set_busy(True)
        self._emit("\n$ " + " ".join(shlex.quote(x) for x in argv), "cmd")
        threading.Thread(target=self._work_raw, args=(argv,), daemon=True).start()

    def _work_raw(self, argv):
        try:
            proc = subprocess.Popen(argv, stdout=subprocess.PIPE,
                                    stderr=subprocess.STDOUT, text=True,
                                    bufsize=1, encoding="utf-8",
                                    errors="replace",
                                    env=dict(os.environ,
                                             PYTHONIOENCODING="utf-8:replace"))
            for line in proc.stdout:
                line = line.rstrip("\n")
                if line.strip():
                    self._emit(line)
            proc.wait()
            self._emit("[fin] {}".format(
                "OK" if proc.returncode == 0 else
                "codigo {}".format(proc.returncode)),
                "ok" if proc.returncode == 0 else "err")
        except Exception as e:
            self._emit("[e] {}".format(e), "err")
        finally:
            self.q.put(("", "__done__"))

    def _launch(self, argv):
        """Lanza una herramienta de libs/ en un hilo, con lista de argumentos."""
        if self.busy:
            return
        self._set_busy(True)
        self._emit("\n$ python3 " + " ".join(shlex.quote(x) for x in argv), "cmd")
        threading.Thread(target=self._work, args=(argv,), daemon=True).start()

    def _work(self, argv):
        try:
            entorno = dict(os.environ, PYTHONIOENCODING="utf-8:replace")
            proc = subprocess.Popen([sys.executable] + argv,
                                    stdout=subprocess.PIPE,
                                    stderr=subprocess.STDOUT,
                                    cwd=APP_DIR, text=True, bufsize=1,
                                    encoding="utf-8", errors="replace",
                                    env=entorno)
            for line in proc.stdout:
                line = line.rstrip("\n")
                if line.strip():
                    tag = "err" if line.startswith("[e]") else (
                        "ok" if line.startswith("[-]") else None)
                    self._emit(line, tag)
            proc.wait()
            if proc.returncode == 0:
                self._emit("[fin] " + self.T("fin_ok"), "ok")
            else:
                self._emit("[fin] " + self.T("fin_code").format(proc.returncode), "err")
        except Exception as e:
            self._emit("[e] " + self.T("err_exec").format(e), "err")
        finally:
            self.q.put(("", "__done__"))


if __name__ == "__main__":
    WhapaGUI().mainloop()
