import customtkinter as ctk
from Process import process
from threading import Thread

bgk = '#2B2B2B'


class Window:
    def __init__(self):
        self.window = ctk.CTk(fg_color=bgk)
        self.window.resizable(False, False)
        self.window.title('Busca ML')
        self.progress = ctk.DoubleVar()
        self.progress.set(0)
        self.frame_pai = ctk.CTkFrame(self.window, fg_color='transparent')
        self.config()
        self.window.grid_rowconfigure(0, weight=1)
        self.window.grid_columnconfigure(0, weight=1)
        self.window_inicial()

        self.window.mainloop()

    def config(self):
        self.frame_pai.columnconfigure(0, weight=1)
        self.frame_pai.columnconfigure(1, weight=1)
        self.frame_pai.rowconfigure(0, weight=1)
        self.frame_pai.rowconfigure(1, weight=2)

    def window_inicial(self):

        lista_p_chave = []
        lista_p_chave_exc = []

        def add_p_chave(entry):
            p_chave = entry.get().lower()
            lista_p_chave.append(p_chave)
            string = self.lbl_p_chave_sel.cget('text')
            string = f'{string} "{p_chave}"'
            self.lbl_p_chave_sel.configure(text=string)

        def add_p_chave_exc(entry):
            p_chave = entry.get().lower()
            lista_p_chave_exc.append(p_chave)
            string = self.lbl_p_chave_exc_sel.cget('text')
            string = f'{string} "{p_chave}"'
            self.lbl_p_chave_exc_sel.configure(text=string)

        def iniciar_pequisa(entry_prod):
            nome_produto = entry_prod.get()

            self.loading(nome_produto, lista_p_chave, lista_p_chave_exc, var_arq_pdr.get())

        self.window.geometry('700x400')

        frame_d = ctk.CTkFrame(self.frame_pai)
        frame_e = ctk.CTkFrame(self.frame_pai)
        lbl_welcome = ctk.CTkLabel(self.frame_pai, text='Bem vindo ao Busca ML',font=('Arial', 25))

        # frame_e
        lbl_digite = ctk.CTkLabel(frame_e, text='Digite o nome do produto a ser buscado:', font=('Arial', 15))
        entry_produto = ctk.CTkEntry(frame_e, placeholder_text='Nome do produto',
                                     width=270,height=38)
        lbl_p_chave = ctk.CTkLabel(frame_e, text='Digite as palavras-chave:', font=('Arial', 15))
        entry_p_chave = ctk.CTkEntry(frame_e, width=150, height=38, placeholder_text='Palavras-chave')
        self.lbl_p_chave_sel = ctk.CTkLabel(frame_e, text='')
        btn_p_chave = ctk.CTkButton(frame_e, text='Add\n palavra-chave',command=lambda:add_p_chave(entry_p_chave))
        space_e = ctk.CTkLabel(frame_e, text='')

        # frame_d
        lbl_p_chave_exc = ctk.CTkLabel(frame_d, text='Digite as palavras-chave exclusoras:', font=('Arial', 15))
        entry_p_chave_exc = ctk.CTkEntry(frame_d, placeholder_text='Palavras-chave exclusoras',
                                         width=150,height=38)
        self.lbl_p_chave_exc_sel = ctk.CTkLabel(frame_d, text='')
        btn_p_chave_exc = ctk.CTkButton(frame_d, text='Add palavra-chave\n exclusora',
                                        command=lambda:add_p_chave_exc(entry_p_chave_exc))
        var_arq_pdr = ctk.IntVar()
        arquivo_padrao = ctk.CTkCheckBox(frame_d, text='Substituir arquivo mestre', variable=var_arq_pdr,
                                         onvalue=1, offvalue=0)
        btn_concluir = ctk.CTkButton(frame_d, text='Pesquisar', command=lambda: iniciar_pequisa(entry_produto))

        # Principais
        self.frame_pai.grid(row=0, column=0)
        lbl_welcome.grid(row=0, column=0, columnspan=2, pady=(0,50))
        frame_e.grid(row=1, column=0)
        frame_d.grid(row=1, column=1, padx=10)

        # frame_e
        lbl_digite.grid(row=0,column=0, columnspan=2)
        entry_produto.grid(row=1,column=0, columnspan=2)
        space_e.grid(row=2)
        lbl_p_chave.grid(row=3,column=0, columnspan=2)
        entry_p_chave.grid(row=4,column=0, padx=10)
        btn_p_chave.grid(row=4, column=1)
        self.lbl_p_chave_sel.grid(row=5,columnspan=2)

        # frame_d
        lbl_p_chave_exc.grid(row=0, column=0, columnspan=2)
        entry_p_chave_exc.grid(row=1, column=0, padx=10)
        btn_p_chave_exc.grid(row=1, column=1)
        self.lbl_p_chave_exc_sel.grid(row=2, column=0, columnspan=2)
        btn_concluir.grid(row=4,column=1)
        arquivo_padrao.grid(row=3, column=1, pady=10)

    def limpa_tela(self):
        self.frame_pai.destroy()
        self.frame_pai = ctk.CTkFrame(self.window, fg_color='transparent')

    def loading(self, nome_produto, lista_p_chave, lista_p_chave_exc, arquivo_padrao):
        self.limpa_tela()
        self.window.geometry('600x240')
        self.window.rowconfigure(0, weight=2)
        self.window.rowconfigure(1, weight=1)

        progressbar = ctk.CTkProgressBar(self.window, variable=self.progress, width=350, height=40)
        txt_lbl = ctk.StringVar()
        txt_lbl.set('Iniciando Busca')
        lbl = ctk.CTkLabel(self.window, textvariable=txt_lbl)
        progressbar.grid(row=0)
        lbl.grid(row=1)

        t = Thread(target=lambda: process(
            nome_produto=nome_produto, palavras_chave=lista_p_chave,
            palavras_chave_exclusora=lista_p_chave_exc,
            progress=self.progress, lbl=txt_lbl, arquivo_padrao=arquivo_padrao))
        t.start()


Window()