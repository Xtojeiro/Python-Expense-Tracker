import json
from datetime import datetime, timedelta
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
import csv
import calendar

class ModernFinanceApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Finanças Pessoais Modernas")
        self.geometry("1400x900")
        self.configure(bg='#f5f6fa')
        
        self.gerenciador = FinanceManager()
        self.current_theme = 'light'
        self.setup_ui()
        
    def setup_ui(self):
        # Configurar estilo
        self.style = ttk.Style()
        self.style.theme_use('clam')
        self.configure_styles()
        
        # Container principal
        main_container = ttk.PanedWindow(self, orient=tk.HORIZONTAL)
        main_container.pack(fill=tk.BOTH, expand=True)
        
        # Sidebar
        self.sidebar = ttk.Frame(main_container, width=250, style='Sidebar.TFrame')
        main_container.add(self.sidebar)
        
        # Conteúdo principal
        self.main_content = ttk.Frame(main_container, style='Main.TFrame')
        main_container.add(self.main_content, weight=1)
        
        self.build_sidebar()
        self.build_dashboard()
        
    def configure_styles(self):
        style_config = {
            'TFrame': {'background': '#ffffff'},
            'Sidebar.TFrame': {'background': '#2c3e50'},
            'Main.TFrame': {'background': '#f5f6fa'},
            'TButton': {
                'font': ('Arial', 10),
                'padding': 10,
                'background': '#3498db',
                'foreground': 'white'
            },
            'Menu.TButton': {
                'font': ('Arial', 12),
                'padding': (20, 15),
                'width': 20,
                'background': '#2c3e50',
                'foreground': '#ecf0f1'
            },
            'TLabel': {'font': ('Arial', 12)},
            'Header.TLabel': {'font': ('Arial', 18, 'bold')}
        }
        
        for style, config in style_config.items():
            self.style.configure(style, **config)
            
    def build_sidebar(self):
        logo_frame = ttk.Frame(self.sidebar)
        logo_frame.pack(pady=20)
        
        ttk.Label(logo_frame, text="💰 Finanças", style='Header.TLabel', 
                foreground='#ecf0f1', background='#2c3e50').pack()
        
        menu_options = [
            ('📊 Dashboard', self.show_dashboard),
            ('💸 Transações', self.show_transactions),
            ('📅 Planejamento', self.show_budgets),
            ('📈 Relatórios', self.show_reports),
            ('⚙ Configurações', self.show_settings)
        ]
        
        for text, command in menu_options:
            btn = ttk.Button(self.sidebar, text=text, style='Menu.TButton', 
                           command=command)
            btn.pack(pady=5, padx=10, fill=tk.X)
            
        ttk.Separator(self.sidebar, orient=tk.HORIZONTAL).pack(fill=tk.X, pady=20)
        
        quick_add = ttk.Button(self.sidebar, text="➕ Adição Rápida", 
                             command=self.quick_add_window)
        quick_add.pack(pady=5, padx=10)
        
    def build_dashboard(self):
        self.dashboard_frame = ttk.Frame(self.main_content)
        
        # Cards resumo
        cards_frame = ttk.Frame(self.dashboard_frame)
        cards_frame.pack(fill=tk.X, padx=20, pady=20)
        
        self.summary_cards = {
            'total_gasto': self.create_summary_card(cards_frame, "Total Gasto", "R$ 0,00", '#e74c3c'),
            'saldo_atual': self.create_summary_card(cards_frame, "Saldo Disponível", "R$ 0,00", '#2ecc71'),
            'orcamento': self.create_summary_card(cards_frame, "Orçamento Restante", "R$ 0,00", '#f1c40f')
        }
        
        # Gráficos
        charts_frame = ttk.Frame(self.dashboard_frame)
        charts_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        self.fig = Figure(figsize=(10, 6), dpi=100)
        self.chart_canvas = FigureCanvasTkAgg(self.fig, master=charts_frame)
        self.chart_canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        
    def create_summary_card(self, parent, title, value, color):
        frame = ttk.Frame(parent, style='Card.TFrame')
        frame.pack(side=tk.LEFT, expand=True, fill=tk.BOTH, padx=10)
        
        ttk.Label(frame, text=title, style='CardTitle.TLabel').pack(pady=5)
        ttk.Label(frame, text=value, style='CardValue.TLabel').pack(pady=10)
        return frame
        
    def show_dashboard(self):
        self.clear_main_content()
        self.dashboard_frame.pack(fill=tk.BOTH, expand=True)
        self.update_dashboard()
        
    def update_dashboard(self):
        # Atualizar dados dos cards
        total_gasto = sum(t['valor'] for t in self.gerenciador.transacoes)
        self.summary_cards['total_gasto'].children['!label2'].config(text=f"R$ {total_gasto:,.2f}")
        
        # Atualizar gráficos
        self.fig.clear()
        ax = self.fig.add_subplot(111)
        
        categorias = {}
        for t in self.gerenciador.transacoes:
            categorias[t['categoria']] = categorias.get(t['categoria'], 0) + t['valor']
            
        if categorias:
            ax.pie(categorias.values(), labels=categorias.keys(), autopct='%1.1f%%')
            ax.set_title('Distribuição por Categoria')
            self.chart_canvas.draw()
            
    def show_transactions(self):
        self.clear_main_content()
        frame = ttk.Frame(self.main_content)
        frame.pack(fill=tk.BOTH, expand=True)
        
        # Filtros
        filter_frame = ttk.Frame(frame)
        filter_frame.pack(fill=tk.X, padx=20, pady=10)
        
        ttk.Label(filter_frame, text="Filtrar por:").pack(side=tk.LEFT)
        self.filter_category = ttk.Combobox(filter_frame, values=self.gerenciador.categorias)
        self.filter_category.pack(side=tk.LEFT, padx=10)
        
        ttk.Label(filter_frame, text="Período:").pack(side=tk.LEFT)
        self.filter_period = ttk.Combobox(filter_frame, values=['Últimos 7 dias', 'Este mês', 'Personalizado'])
        self.filter_period.pack(side=tk.LEFT, padx=10)
        
        btn_filter = ttk.Button(filter_frame, text="Aplicar Filtros", command=self.apply_filters)
        btn_filter.pack(side=tk.LEFT, padx=10)
        
        # Tabela de transações
        columns = ('Data', 'Categoria', 'Valor', 'Descrição', 'Recorrente')
        self.transaction_table = ttk.Treeview(frame, columns=columns, show='headings')
        
        for col in columns:
            self.transaction_table.heading(col, text=col)
            self.transaction_table.column(col, width=120)
            
        scroll = ttk.Scrollbar(frame, orient=tk.VERTICAL, command=self.transaction_table.yview)
        self.transaction_table.configure(yscroll=scroll.set)
        
        self.transaction_table.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        scroll.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.load_transactions()
        
    def apply_filters(self):
        # Implementar lógica de filtragem
        self.load_transactions()
        
    def load_transactions(self):
        for item in self.transaction_table.get_children():
            self.transaction_table.delete(item)
            
        for t in self.gerenciador.transacoes:
            values = (
                datetime.fromisoformat(t['data']).strftime('%d/%m/%Y'),
                t['categoria'],
                f"R$ {t['valor']:.2f}",
                t['descricao'],
                'Sim' if t.get('recorrente', False) else 'Não'
            )
            self.transaction_table.insert('', tk.END, values=values)
            
    def quick_add_window(self):
        window = tk.Toplevel(self)
        window.title("Adição Rápida")
        
        ttk.Label(window, text="Valor:").grid(row=0, column=0, padx=5, pady=5)
        valor = ttk.Entry(window)
        valor.grid(row=0, column=1)
        
        ttk.Label(window, text="Categoria:").grid(row=1, column=0)
        categoria = ttk.Combobox(window, values=self.gerenciador.categorias)
        categoria.grid(row=1, column=1)
        
        ttk.Label(window, text="Descrição:").grid(row=2, column=0)
        descricao = ttk.Entry(window)
        descricao.grid(row=2, column=1)
        
        recorrente = tk.BooleanVar()
        ttk.Checkbutton(window, text="Recorrente", variable=recorrente).grid(row=3, columnspan=2)
        
        ttk.Button(window, text="Salvar", command=lambda: self.save_transaction(
            valor.get(),
            categoria.get(),
            descricao.get(),
            recorrente.get()
        )).grid(row=4, columnspan=2, pady=10)
        
    def save_transaction(self, valor, categoria, descricao, recorrente):
        try:
            if not valor or not categoria:
                raise ValueError("Campos obrigatórios faltando")
                
            transaction = {
                'data': datetime.now().isoformat(),
                'valor': float(valor),
                'categoria': categoria,
                'descricao': descricao,
                'recorrente': recorrente
            }
            
            self.gerenciador.add_transaction(transaction)
            self.update_dashboard()
            messagebox.showinfo("Sucesso", "Transação salva com sucesso!")
        except ValueError as e:
            messagebox.showerror("Erro", str(e))
            
    def clear_main_content(self):
        for widget in self.main_content.winfo_children():
            widget.destroy()
            
    def show_budgets(self):
        # Implementar interface de orçamentos
        pass
        
    def show_reports(self):
        # Implementar relatórios avançados
        pass
        
    def show_settings(self):
        # Implementar configurações
        pass

class FinanceManager:
    def __init__(self, file='data.json'):
        self.file = file
        self.transacoes = []
        self.categorias = []
        self.load_data()
        
    def load_data(self):
        try:
            with open(self.file, 'r') as f:
                data = json.load(f)
                self.transacoes = data.get('transacoes', [])
                self.categorias = list(set(t['categoria'] for t in self.transacoes))
        except FileNotFoundError:
            self.transacoes = []
            self.categorias = []
            
    def save_data(self):
        data = {
            'transacoes': self.transacoes,
            'categorias': self.categorias
        }
        with open(self.file, 'w') as f:
            json.dump(data, f, indent=4)
            
    def add_transaction(self, transaction):
        self.transacoes.append(transaction)
        if transaction['categoria'] not in self.categorias:
            self.categorias.append(transaction['categoria'])
        self.save_data()
            
if __name__ == "__main__":
    app = ModernFinanceApp()
    app.mainloop()