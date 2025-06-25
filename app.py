# Importação das bibliotecas necessárias
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import numpy as np

# Configuração da página do Streamlit
st.set_page_config(
    page_title="Painel de Análise de Cursos",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Estilização CSS personalizada para melhorar a aparência visual
st.markdown("""
<style>
    /* Estilos gerais */
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
    }
    
    /* Estilos para métricas */
    .metric-container {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        margin: 0.5rem 0;
    }
    .stMetric {
        margin-bottom: 1rem;
        text-align: center !important;
        align-items: center !important;
        justify-content: center !important;
    }
    .stMetric [data-testid="stMetricValue"] {
        font-size: 2rem;
        text-align: center !important;
        width: 100%;
        display: block;
    }
    .stMetric [data-testid="stMetricLabel"] {
        font-size: 1.2rem;
        text-align: center !important;
        width: 100%;
        display: block;
    }
    
    /* Estilos para gráficos */
    .stPlotlyChart {
        margin-top: 1rem;
    }
    .js-plotly-plot .plotly .gtitle,
    .js-plotly-plot .plotly .g-gtitle text,
    .stPlotlyChart .plotly-graph-div .gtitle {
        text-anchor: middle !important;
    }
    
    /* Estilos para tabelas */
    .stDataFrame table,
    .stTable table,
    div[data-testid="stTable"] table {
        margin: 0 auto !important;
    }
    .stDataFrame table thead tr th,
    .stTable table th,
    div[data-testid="stTable"] th {
        text-align: center !important;
        vertical-align: middle !important;
    }
    .stDataFrame table tbody tr td,
    .stTable table td,
    div[data-testid="stTable"] td {
        text-align: center !important;
        vertical-align: middle !important;
    }
    
    /* Estilos para abas */
    .stTabs [data-baseweb="tab-list"] {
        gap: 2rem;
    }
</style>
""", unsafe_allow_html=True)

# Função para carregar os dados dos arquivos CSV
@st.cache_data
def load_data():
    """
    Carrega os dados dos arquivos CSV necessários para o dashboard.
    
    Returns:
        tuple: (DataFrame com dados históricos, DataFrame com previsões) ou (None, None) em caso de erro
    """
    try:
        df = pd.read_csv('cleaned_data.csv')
        predictions = pd.read_csv('predictions_2025.csv')
        return df, predictions
    except FileNotFoundError:
        st.error("❌ Arquivo 'cleaned_data.csv' ou 'predictions_2025.csv' não encontrado. Por favor, faça upload dos seus conjuntos de dados.")
        return None, None

def create_metric_columns(course_data, predictions, selected_course):
    """
    Cria e exibe as métricas principais para um curso.
    
    Args:
        course_data (DataFrame): Dados históricos do curso
        predictions (DataFrame): Previsões para 2025
        selected_course (str): ID do curso selecionado
    """
    avg_occupancy = course_data['taxa_ocupacao'].mean() * 100
    avg_grade = course_data['nota_ultimo_colocado'].mean()
    most_recent_year = course_data.iloc[-1]
    last_grade = most_recent_year['nota_ultimo_colocado']
    last_placed = most_recent_year['colocados']
    course_predictions = predictions[predictions['course_id'] == selected_course]
    has_predictions = not course_predictions.empty

    metrics_cols = st.columns(6)
    metrics_cols[0].metric("Taxa Média de Ocupação", f"{avg_occupancy:.0f}%")
    metrics_cols[1].metric("Nota Média do Último Colocado", f"{avg_grade:.1f}")
    metrics_cols[2].metric(f"Nota do Último Colocado ({int(most_recent_year['ano'])})", f"{last_grade:.1f}")
    metrics_cols[3].metric(f"Alunos Colocados ({int(most_recent_year['ano'])})", f"{int(last_placed)}")
    
    if has_predictions:
        metrics_cols[4].metric("Previsão Nota do Último Colocado 2025", f"{course_predictions['nota_ultimo_colocado_prevista'].iloc[0]:.1f}")
        metrics_cols[5].metric("Previsão Alunos Colocados 2025", f"{int(course_predictions['colocados_previsto'].iloc[0])}")
    else:
        metrics_cols[4].empty()
        metrics_cols[5].empty()

def create_evolution_charts(course_data):
    """
    Cria os gráficos de evolução para um curso.
    
    Args:
        course_data (DataFrame): Dados históricos do curso
    
    Returns:
        tuple: (fig1, fig2) - Figuras Plotly para número de colocados e nota do último colocado
    """
    # Gráfico de número de colocados
    fig1 = px.line(
        course_data, 
        x='ano', 
        y='colocados',
        title='Número de Colocados ao Longo do Tempo',
        markers=True,
        line_shape='spline'
    )
    fig1.update_layout(
        yaxis_title="Número de Colocados",
        xaxis_title="Ano",
        height=250,
        xaxis=dict(tickformat='.0f'),
        margin=dict(t=40, b=30, l=30, r=30),
        title={
            'text': 'Número de Colocados ao Longo do Tempo',
            'x': 0.5,
            'y': 0.95,
            'xanchor': 'center',
            'yanchor': 'top'
        }
    )
    fig1.update_traces(line_color='#1f77b4', marker_size=8)

    # Gráfico de nota do último colocado
    fig2 = px.line(
        course_data, 
        x='ano', 
        y='nota_ultimo_colocado',
        title='Nota do Último Colocado',
        markers=True,
        line_shape='spline'
    )
    fig2.update_layout(
        yaxis_title="Nota",
        xaxis_title="Ano",
        height=250,
        xaxis=dict(tickformat='.0f'),
        margin=dict(t=40, b=30, l=30, r=30),
        title={
            'text': 'Nota do Último Colocado',
            'x': 0.5,
            'y': 0.95,
            'xanchor': 'center',
            'yanchor': 'top'
        }
    )
    fig2.update_traces(line_color='#1f77b4', marker_size=8)

    return fig1, fig2

def create_detailed_table(course_data):
    """
    Cria e exibe a tabela detalhada com os dados do curso.
    
    Args:
        course_data (DataFrame): Dados históricos do curso
    """
    display_data = course_data[[
        'ano', 'vagas_iniciais', 'colocados', 'taxa_ocupacao',
        'nota_ultimo_colocado', 'vagas_sobrantes'
    ]].copy()
    display_data.columns = [
        'Ano', 'Vagas Iniciais', 'Alunos Colocados', 'Taxa de Ocupação',
        'Nota do Último Colocado', 'Vagas Restantes'
    ]
    display_data['Taxa de Ocupação'] = (display_data['Taxa de Ocupação'] * 100).round(0).astype(int).astype(str) + '%'
    display_data['Nota do Último Colocado'] = display_data['Nota do Último Colocado'].round(1)
    display_data['Vagas Iniciais'] = display_data['Vagas Iniciais'].astype(int)
    display_data['Alunos Colocados'] = display_data['Alunos Colocados'].astype(int)
    display_data['Vagas Restantes'] = display_data['Vagas Restantes'].astype(int)
    display_data = display_data.reset_index(drop=True)
    st.table(display_data)

def create_course_evolution_view(df, predictions, selected_course, year_range):
    """
    Cria visualizações da evolução do curso ao longo do tempo.
    
    Args:
        df (DataFrame): DataFrame com dados históricos
        predictions (DataFrame): DataFrame com previsões
        selected_course (str): ID do curso selecionado
        year_range (tuple): Tupla com (ano_inicial, ano_final)
    """
    # Filtra dados para o curso e período selecionados
    course_data = df[
        (df['course_id'] == selected_course) & 
        (df['ano'] >= year_range[0]) & 
        (df['ano'] <= year_range[1])
    ].sort_values('ano')
    
    if course_data.empty:
        st.warning("Nenhum dado encontrado para o curso e período selecionados.")
        return
    
    # Obtém informações do curso
    course_name = course_data['curso'].iloc[0]
    university_name = course_data['nome_universidade'].iloc[0]
    faculty_name = course_data['nome_faculdade'].iloc[0]
    
    st.markdown(f"### 📈 Análise de Evolução: {course_name}")
    st.markdown(f"**Universidade:** {university_name}")
    st.markdown(f"**Faculdade:** {faculty_name}")

    # Exibe métricas principais
    st.markdown("#### 📊 Métricas Principais")
    create_metric_columns(course_data, predictions, selected_course)

    # Cria gráficos lado a lado
    chart_col1, chart_col2 = st.columns(2)
    fig1, fig2 = create_evolution_charts(course_data)
    
    with chart_col1:
        st.plotly_chart(fig1, use_container_width=True)
    with chart_col2:
        st.plotly_chart(fig2, use_container_width=True)

    # Exibe tabela detalhada em um expander
    with st.expander('📋 Dados Detalhados', expanded=False):
        create_detailed_table(course_data)

def create_comparison_chart(historical_data, predictions, selected_courses, y_column, title, y_axis_title):
    """
    Cria um gráfico de comparação para múltiplos cursos.
    
    Args:
        historical_data (DataFrame): Dados históricos dos cursos
        predictions (DataFrame): Previsões para 2025
        selected_courses (list): Lista de IDs dos cursos selecionados
        y_column (str): Nome da coluna a ser plotada no eixo y
        title (str): Título do gráfico
        y_axis_title (str): Título do eixo y
    
    Returns:
        Figure: Figura Plotly com o gráfico de comparação
    """
    fig = go.Figure()
    
    # Adiciona linha vertical para 2024
    fig.add_vline(
        x=2024,
        line_dash="dash",
        line_color="gray",
        opacity=0.5,
        annotation_text="Previsão 2025",
        annotation_position="top right"
    )
    
    # Adiciona dados históricos para cada curso
    for course in selected_courses:
        course_data = historical_data[historical_data['course_id'] == course]
        course_name = course_data['curso'].iloc[0]
        
        # Obtém o último ponto histórico
        last_year = course_data['ano'].max()
        last_value = course_data[course_data['ano'] == last_year][y_column].iloc[0]
        
        # Cria uma cor para este curso
        line_color = px.colors.qualitative.Set1[len(fig.data) % len(px.colors.qualitative.Set1)]
        
        # Adiciona linha histórica
        fig.add_trace(go.Scatter(
            x=course_data['ano'],
            y=course_data[y_column],
            name=course_name,
            mode='lines+markers',
            line=dict(shape='spline', color=line_color),
            marker=dict(size=8)
        ))
        
        # Adiciona previsão se disponível
        course_pred = predictions[predictions['course_id'] == course]
        if not course_pred.empty:
            # Mapeia o nome da coluna para o formato correto das previsões
            prediction_column = {
                'colocados': 'colocados_previsto',
                'nota_ultimo_colocado': 'nota_ultimo_colocado_prevista'
            }[y_column]
            
            pred_value = course_pred[prediction_column].iloc[0]
            # Adiciona linha de previsão como continuação
            fig.add_trace(go.Scatter(
                x=[last_year, 2025],
                y=[last_value, pred_value],
                name=f"{course_name} (Previsão)",
                mode='lines+markers',
                line=dict(
                    dash='dot',
                    width=2,
                    color=line_color
                ),
                marker=dict(
                    size=8,
                    symbol='circle',
                    color=line_color
                ),
                showlegend=False
            ))
    
    fig.update_layout(
        yaxis_title=y_axis_title,
        xaxis_title="Ano",
        height=300,
        xaxis=dict(tickformat='.0f'),
        margin=dict(t=40, b=30, l=30, r=30),
        title={
            'text': title,
            'x': 0.5,
            'y': 0.95,
            'xanchor': 'center',
            'yanchor': 'top'
        },
        legend=dict(
            yanchor="top",
            y=0.99,
            xanchor="left",
            x=1.05
        )
    )
    
    return fig

def create_comparison_summary(df, predictions, selected_courses, selected_years):
    """
    Cria um resumo comparativo dos cursos selecionados para os anos especificados.
    
    Args:
        df (DataFrame): DataFrame com dados históricos
        predictions (DataFrame): DataFrame com previsões
        selected_courses (list): Lista de IDs dos cursos selecionados
        selected_years (list): Lista de anos para o resumo
    
    Returns:
        DataFrame: Resumo comparativo formatado
    """
    summary_dataframes = []
    
    for selected_year in selected_years:
        # Filtra dados para o ano selecionado
        year_data = df[
            (df['course_id'].isin(selected_courses)) & 
            (df['ano'] == selected_year)
        ]
        
        # Se o ano selecionado for 2025, usa previsões
        if selected_year == 2025:
            year_summary = pd.DataFrame()
            for course in selected_courses:
                course_pred = predictions[predictions['course_id'] == course]
                if not course_pred.empty:
                    course_data = df[df['course_id'] == course].iloc[0]
                    year_summary = pd.concat([year_summary, pd.DataFrame({
                        'Curso': [course_data['curso']],
                        'Ano': [2025],
                        'Ocupação %': ['Previsão'],
                        'Nota Mínima': [course_pred['nota_ultimo_colocado_prevista'].iloc[0].round(1)],
                        'Vagas Restantes': ['Previsão']
                    })])
        else:
            year_summary = year_data[['curso', 'ano', 'taxa_ocupacao', 'nota_ultimo_colocado', 'vagas_sobrantes']].copy()
            year_summary.columns = ['Curso', 'Ano', 'Ocupação %', 'Nota Mínima', 'Vagas Restantes']
            
            # Formata porcentagem sem decimais
            year_summary['Ocupação %'] = (year_summary['Ocupação %'] * 100).round(0).astype(int).astype(str) + '%'
            year_summary['Nota Mínima'] = year_summary['Nota Mínima'].round(1)
            year_summary['Ano'] = year_summary['Ano'].astype(int)
        
        summary_dataframes.append(year_summary)
    
    # Combina todos os resumos de anos
    if summary_dataframes:
        return pd.concat(summary_dataframes, ignore_index=True)
    return None

def create_course_comparison_view(df, selected_courses, predictions):
    """
    Cria visualizações de comparação entre cursos.
    
    Args:
        df (DataFrame): DataFrame com dados históricos
        selected_courses (list): Lista de IDs dos cursos selecionados
        predictions (DataFrame): DataFrame com previsões
    """
    # Obtém dados históricos dos cursos selecionados
    historical_data = df[df['course_id'].isin(selected_courses)]
    
    if historical_data.empty:
        st.warning("Nenhum dado encontrado para os cursos selecionados.")
        return
    
    st.markdown(f"### 🔍 Comparação de Cursos")
    
    # Cria gráficos de linha para comparação histórica
    st.markdown("#### 📈 Evolução Histórica dos Cursos Selecionados")
    chart_col1, chart_col2 = st.columns(2)
    
    with chart_col1:
        fig_evolution = create_comparison_chart(
            historical_data,
            predictions,
            selected_courses,
            'colocados',
            'Evolução do Número de Colocados',
            'Número de Colocados'
        )
        st.plotly_chart(fig_evolution, use_container_width=True)
    
    with chart_col2:
        fig_grades = create_comparison_chart(
            historical_data,
            predictions,
            selected_courses,
            'nota_ultimo_colocado',
            'Evolução da Nota do Último Colocado',
            'Nota'
        )
        st.plotly_chart(fig_grades, use_container_width=True)
    
    # Tabela resumo com seleção de ano
    st.markdown("#### 📋 Resumo da Comparação")
    
    # Obtém anos disponíveis para os cursos selecionados
    available_years = sorted(historical_data['ano'].unique(), reverse=True)
    
    # Adiciona seleção de ano
    selected_years = st.multiselect(
        "Selecione os Anos para o Resumo",
        available_years,
        default=[available_years[0]],
        key="comparison_years_selector"
    )
    
    if not selected_years:
        st.info("Por favor, selecione pelo menos um ano para visualizar o resumo.")
        return
    
    # Cria e exibe o resumo comparativo
    final_summary = create_comparison_summary(df, predictions, selected_courses, selected_years)
    if final_summary is not None:
        st.dataframe(
            final_summary,
            use_container_width=True,
            height=250,
            hide_index=True,
            column_config={
                "Curso": st.column_config.TextColumn(
                    "Curso",
                    help="Nome do curso",
                    width="medium",
                ),
                "Ano": st.column_config.NumberColumn(
                    "Ano",
                    help="Ano dos dados",
                    width="small",
                    format="%d",
                ),
                "Ocupação %": st.column_config.TextColumn(
                    "Ocupação %",
                    help="Taxa de ocupação do curso",
                    width="small",
                ),
                "Nota Mínima": st.column_config.NumberColumn(
                    "Nota Mínima",
                    help="Nota do último colocado",
                    width="small",
                    format="%.1f",
                ),
                "Vagas Restantes": st.column_config.TextColumn(
                    "Vagas Restantes",
                    help="Número de vagas não preenchidas",
                    width="small",
                ),
            }
        )

def create_course_selection_ui(df, tab_key=""):
    """
    Cria a interface de seleção de curso com filtros de universidade e faculdade.
    
    Args:
        df (DataFrame): DataFrame com dados históricos
        tab_key (str): Sufixo para as chaves dos componentes Streamlit
    
    Returns:
        tuple: (selected_university, selected_faculty, selected_course)
    """
    # Cria colunas para seleção hierárquica
    col1, col2, col3 = st.columns(3)
    
    with col1:
        # Seleção de universidade
        universities_data = df['nome_universidade'].dropna().unique()
        universities = sorted(universities_data.tolist(), reverse=True)
        selected_university = st.selectbox(
            "Selecione a Universidade",
            universities,
            index=universities.index('Universidade de Lisboa') if 'Universidade de Lisboa' in universities else 0,
            key=f"university_{tab_key}"
        )
    
    with col2:
        # Seleção de faculdade baseada na universidade selecionada
        faculties_data = df[df['nome_universidade'] == selected_university]['nome_faculdade'].dropna().unique()
        faculties = sorted(faculties_data.tolist(), reverse=True)
        selected_faculty = st.selectbox(
            "Selecione a Faculdade",
            faculties,
            index=faculties.index('Instituto Superior de Economia e Gestão') if 'Instituto Superior de Economia e Gestão' in faculties else 0,
            key=f"faculty_{tab_key}"
        )
    
    with col3:
        # Seleção de curso baseada na universidade e faculdade selecionadas
        courses = df[
            (df['nome_universidade'] == selected_university) & 
            (df['nome_faculdade'] == selected_faculty)
        ]
        
        # Remove duplicados baseados no course_id para evitar cursos repetidos
        courses_unique = courses.drop_duplicates(subset=['course_id']).sort_values('curso')
        course_options = courses_unique.set_index('course_id')['curso'].to_dict()
        
        selected_course = st.selectbox(
            "Selecione o Curso",
            options=list(course_options.keys()),
            format_func=lambda x: course_options[x],
            key=f"course_{tab_key}"
        )
    
    return selected_university, selected_faculty, selected_course

def create_course_comparison_ui(df, selected_course):
    """
    Cria a interface para gerenciar a lista de cursos para comparação.
    
    Args:
        df (DataFrame): DataFrame com dados históricos
        selected_course (str): ID do curso selecionado
    
    Returns:
        list: Lista atualizada de cursos selecionados
    """
    # Inicializa a lista de cursos selecionados se não existir
    if 'selected_courses' not in st.session_state:
        # Inicializa com cursos padrão se existirem
        default_courses = df[
            (df['nome_universidade'] == 'Universidade de Lisboa') &
            (df['nome_faculdade'] == 'Instituto Superior de Economia e Gestão') &
            (df['curso'].isin(['Economia', 'Gestão']))
        ]['course_id'].unique().tolist()  # Use unique() to avoid duplicates
        st.session_state.selected_courses = default_courses
    
    # Adiciona curso selecionado à lista se não estiver presente
    if selected_course and selected_course not in st.session_state.selected_courses:
        if st.button("Adicionar Curso à Comparação"):
            st.session_state.selected_courses.append(selected_course)
            st.rerun()
    
    # Exibe e gerencia cursos selecionados
    if st.session_state.selected_courses:
        st.markdown("#### Cursos Selecionados para Comparação")
        
        # Remove duplicates from selected courses
        st.session_state.selected_courses = list(dict.fromkeys(st.session_state.selected_courses))
        
        # Cria um dicionário com informações dos cursos para evitar consultas repetidas
        course_info = {}
        for course_id in st.session_state.selected_courses:
            course_data = df[df['course_id'] == course_id].iloc[0]
            course_info[course_id] = {
                'curso': course_data['curso'],
                'universidade': course_data['nome_universidade'],
                'faculdade': course_data['nome_faculdade'] if pd.notna(course_data['nome_faculdade']) else 'N/A'
            }
        
        selected_courses_display = [
            f"{course_info[course_id]['curso']} ({course_info[course_id]['universidade']} - {course_info[course_id]['faculdade']})"
            for course_id in st.session_state.selected_courses
        ]
        
        # Cria uma linha para cada curso selecionado com botão de remover
        for i, (course_id, display_name) in enumerate(zip(st.session_state.selected_courses, selected_courses_display)):
            col1, col2 = st.columns([0.9, 0.1])
            with col1:
                st.write(display_name)
            with col2:
                if st.button("❌", key=f"remove_{i}"):
                    st.session_state.selected_courses.remove(course_id)
                    st.rerun()
        
        # Botão para limpar todos
        if st.button("Limpar Todos os Cursos"):
            st.session_state.selected_courses = []
            st.rerun()
    
    return st.session_state.selected_courses

def main():
    """
    Função principal que controla o fluxo da aplicação.
    """
    st.markdown('<h1 class="main-header">🎓 Painel de Análise de Cursos</h1>', unsafe_allow_html=True)
    
    # Carrega os dados
    df, predictions = load_data()
    if df is None:
        return
    
    # Cria abas principais
    tab1, tab2 = st.tabs(["📈 Evolução do Curso", "🔍 Comparação de Cursos"])
    
    with tab1:
        st.markdown("### Analise o desempenho de um curso ao longo do tempo")
        
        # Seleção de curso para evolução
        selected_university, selected_faculty, selected_course = create_course_selection_ui(df)
        
        if selected_course:
            # Usa intervalo completo de anos para visualização de evolução
            year_range = (int(df['ano'].min()), int(df['ano'].max()))
            create_course_evolution_view(df, predictions, selected_course, year_range)
    
    with tab2:
        st.markdown("### Compare múltiplos cursos")
        
        # Seleção de curso para comparação
        selected_university, selected_faculty, selected_course = create_course_selection_ui(df, "tab2")
        
        # Gerencia lista de cursos para comparação
        selected_courses = create_course_comparison_ui(df, selected_course)
        
        if selected_courses:
            create_course_comparison_view(df, selected_courses, predictions)
        else:
            st.info("Selecione cursos para comparar usando os filtros acima.")

if __name__ == "__main__":
    main()#