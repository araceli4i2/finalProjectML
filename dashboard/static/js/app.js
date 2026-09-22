/**
 * LÓGICA CLIENTE: DASHBOARD DE APRENDIZAJE SUPERVISADO (EAIMCS - INE BOLIVIA)
 * Control de navegación SPA, renderizado dinámico con Plotly.js,
 * inferencia interactiva y módulo de monitoreo MLOps.
 */

document.addEventListener('DOMContentLoaded', () => {
  // Estado global de la aplicación
  const state = {
    theme: localStorage.getItem('theme') || 'light',
    activeSection: 'inicio',
    distributionScale: 'log', // 'raw' o 'log'
    distributionData: null,
    dictionaryEntries: [],
    modelsData: null,
    plotlyLayoutBase: {}
  };

  // --------------------------------------------------------------------------
  // 1. GESTIÓN DE TEMA (CLARO / OSCURO)
  // --------------------------------------------------------------------------
  const htmlEl = document.documentElement;
  const themeToggleBtn = document.getElementById('themeToggleBtn');
  const themeIcon = document.getElementById('themeIcon');

  function applyTheme(theme) {
    state.theme = theme;
    htmlEl.setAttribute('data-theme', theme);
    localStorage.setItem('theme', theme);

    if (theme === 'dark') {
      themeIcon.innerHTML = `
        <path d="M21 12.79A9 9 0 1 1 11.21 3 7 7 0 0 0 21 12.79z"></path>
      `;
      state.plotlyLayoutBase = {
        paper_bgcolor: '#1b1b1d',
        plot_bgcolor: '#1b1b1d',
        font: { color: '#c6c6cd', family: 'Inter, sans-serif' },
        xaxis: { gridcolor: '#333335', zerolinecolor: '#45464d' },
        yaxis: { gridcolor: '#333335', zerolinecolor: '#45464d' }
      };
    } else {
      themeIcon.innerHTML = `
        <circle cx="12" cy="12" r="5"></circle>
        <line x1="12" y1="1" x2="12" y2="3"></line>
        <line x1="12" y1="21" x2="12" y2="23"></line>
        <line x1="4.22" y1="4.22" x2="5.64" y2="5.64"></line>
        <line x1="18.36" y1="18.36" x2="19.78" y2="19.78"></line>
        <line x1="1" y1="12" x2="3" y2="12"></line>
        <line x1="21" y1="12" x2="23" y2="12"></line>
        <line x1="4.22" y1="19.78" x2="5.64" y2="18.36"></line>
        <line x1="18.36" y1="5.64" x2="19.78" y2="4.22"></line>
      `;
      state.plotlyLayoutBase = {
        paper_bgcolor: '#ffffff',
        plot_bgcolor: '#ffffff',
        font: { color: '#45464d', family: 'Inter, sans-serif' },
        xaxis: { gridcolor: '#f0edef', zerolinecolor: '#e4e2e4' },
        yaxis: { gridcolor: '#f0edef', zerolinecolor: '#e4e2e4' }
      };
    }

    // Re-renderizar gráficos visibles si ya están cargados
    if (state.activeSection === 'eda') renderEDAPanel();
    if (state.activeSection === 'modelado') renderModeladoPanel();
  }

  themeToggleBtn.addEventListener('click', () => {
    applyTheme(state.theme === 'dark' ? 'light' : 'dark');
  });

  applyTheme(state.theme);

  // --------------------------------------------------------------------------
  // 2. NAVEGACIÓN ENTRE PANELES (SIDEBAR)
  // --------------------------------------------------------------------------
  const navBtns = document.querySelectorAll('.nav-item-btn');
  const panels = document.querySelectorAll('.section-panel');
  const sectionTitle = document.getElementById('currentSectionTitle');
  const sectionSubtitle = document.getElementById('currentSectionSubtitle');

  const titlesMap = {
    'inicio': { title: 'Resumen Ejecutivo', sub: 'Indicadores macroeconómicos y cobertura de empresas bolivianas' },
    'diccionario': { title: 'Diccionario de Datos', sub: 'Variables oficiales según docs/informe/02_diccionario_datos_EAIMCS.md' },
    'eda': { title: 'Análisis Exploratorio (EDA)', sub: 'Distribuciones, boxplots regionales y matriz de correlación' },
    'preprocesamiento': { title: 'Preprocesamiento & Pipeline', sub: 'Limpieza de centinelas 99999, agregación y transformaciones' },
    'modelado': { title: 'Modelado & Resultados', sub: 'Comparativa de algoritmos, residuos e importancia de variables' },
    'prediccion': { title: 'Predicción Interactiva', sub: 'Simulador de ingresos operativos para empresas bolivianas' },
    'mlops': { title: 'MLOps & Monitoreo', sub: 'Gobernanza, registro de versiones y detección de data drift' },
    'acerca': { title: 'Acerca del Proyecto', sub: 'Marco lógico, limitaciones del dataset y fuentes oficiales del INE' }
  };

  navBtns.forEach(btn => {
    btn.addEventListener('click', () => {
      const target = btn.getAttribute('data-section');
      switchSection(target);
    });
  });

  function switchSection(sectionId) {
    state.activeSection = sectionId;

    navBtns.forEach(b => b.classList.toggle('active', b.getAttribute('data-section') === sectionId));
    panels.forEach(p => p.classList.toggle('active', p.id === `panel-${sectionId}`));

    const meta = titlesMap[sectionId] || { title: 'Dashboard', sub: '' };
    sectionTitle.textContent = meta.title;
    sectionSubtitle.textContent = meta.sub;

    // Cargar contenido específico según la sección
    if (sectionId === 'diccionario' && state.dictionaryEntries.length === 0) loadDictionary();
    if (sectionId === 'eda') renderEDAPanel();
    if (sectionId === 'preprocesamiento') loadPipeline();
    if (sectionId === 'modelado') renderModeladoPanel();
    if (sectionId === 'mlops') loadMLOps();

    window.scrollTo({ top: 0, behavior: 'smooth' });
  }

  // Toggle colapsar sidebar
  const sidebarToggle = document.getElementById('sidebarToggle');
  sidebarToggle.addEventListener('click', () => {
    document.body.classList.toggle('sidebar-collapsed');
    window.dispatchEvent(new Event('resize'));
  });

  // --------------------------------------------------------------------------
  // 3. SECCIÓN 1: CARGA DE KPIS
  // --------------------------------------------------------------------------
  async function loadKPIs() {
    try {
      const res = await fetch('/api/kpis');
      const data = await res.json();
      document.getElementById('kpiTotalEmpresas').textContent = Number(data.total_empresas).toLocaleString('es-BO');
      document.getElementById('kpiIngresoMediano').textContent = `Bs ${(data.ingreso_mediano / 1e6).toFixed(2)} M`;
      document.getElementById('kpiIngresoPromedio').textContent = `Bs ${(data.ingreso_promedio / 1e6).toFixed(2)} M`;
      document.getElementById('kpiDeptos').textContent = `${data.num_departamentos} Deptos`;
    } catch (e) {
      console.error('Error al cargar KPIs:', e);
    }
  }
  loadKPIs();

  // --------------------------------------------------------------------------
  // 4. SECCIÓN 2: DICCIONARIO DE DATOS
  // --------------------------------------------------------------------------
  const dictSearchInput = document.getElementById('dictSearchInput');
  const dictSectionFilter = document.getElementById('dictSectionFilter');
  const dictTableBody = document.getElementById('dictionaryTableBody');

  async function loadDictionary() {
    try {
      const res = await fetch('/api/dictionary');
      const data = await res.json();
      state.dictionaryEntries = data.entries;
      renderDictionaryTable(state.dictionaryEntries);
    } catch (e) {
      console.error('Error al cargar diccionario:', e);
      dictTableBody.innerHTML = `<tr><td colspan="5" style="color:red; text-align:center;">Error al cargar el diccionario.</td></tr>`;
    }
  }

  function renderDictionaryTable(entries) {
    if (!entries || entries.length === 0) {
      dictTableBody.innerHTML = `<tr><td colspan="5" style="text-align:center; padding: 2rem; color: var(--text-muted);">No se encontraron variables con los filtros aplicados.</td></tr>`;
      return;
    }

    dictTableBody.innerHTML = entries.map(item => `
      <tr>
        <td><span class="var-tag">${item.name}</span></td>
        <td><strong>${item.section}</strong></td>
        <td>${item.desc}</td>
        <td><span style="font-size: 0.8rem; color: var(--text-secondary);">${item.type}</span></td>
        <td style="font-size: 0.8rem; color: var(--text-muted);">${item.sample}</td>
      </tr>
    `).join('');
  }

  function filterDictionary() {
    const q = dictSearchInput.value.toLowerCase().trim();
    const sec = dictSectionFilter.value.toLowerCase().trim();

    const filtered = state.dictionaryEntries.filter(item => {
      const matchesQ = !q || item.name.toLowerCase().includes(q) || item.desc.toLowerCase().includes(q);
      const matchesSec = !sec || item.section.toLowerCase().includes(sec);
      return matchesQ && matchesSec;
    });
    renderDictionaryTable(filtered);
  }

  dictSearchInput.addEventListener('input', filterDictionary);
  dictSectionFilter.addEventListener('change', filterDictionary);

  // --------------------------------------------------------------------------
  // 5. SECCIÓN 3: ANÁLISIS EXPLORATORIO (EDA)
  // --------------------------------------------------------------------------
  const btnScaleToggle = document.getElementById('btnScaleToggle');
  btnScaleToggle.addEventListener('click', () => {
    state.distributionScale = state.distributionScale === 'log' ? 'raw' : 'log';
    btnScaleToggle.textContent = state.distributionScale === 'log' 
      ? 'Alternar a Escala Natural (Bs)' 
      : 'Alternar a Escala Logarítmica log(1+x)';
    renderDistributionChart();
  });

  async function renderEDAPanel() {
    renderDistributionChart();
    renderBoxplotDeptos();
    renderBoxplotSectors();
    renderCorrelationChart();
    renderOutliersChart();
  }

  async function renderDistributionChart() {
    try {
      if (!state.distributionData) {
        const res = await fetch('/api/eda/distribution');
        state.distributionData = await res.json();
      }

      const isLog = state.distributionScale === 'log';
      const values = isLog ? state.distributionData.log_values : state.distributionData.raw_values;

      const trace = {
        x: values,
        type: 'histogram',
        nbinsx: 35,
        marker: {
          color: isLog ? '#006a61' : '#f97316',
          line: { color: state.theme === 'dark' ? '#090d16' : '#ffffff', width: 1 }
        },
        name: 'Frecuencia'
      };

      const layout = {
        ...state.plotlyLayoutBase,
        title: isLog ? 'Distribución Normalizada en Escala log(1 + Ingresos)' : 'Distribución en Bolivianos Naturales (Sesgo Positivo Severo)',
        xaxis: {
          ...state.plotlyLayoutBase.xaxis,
          title: isLog ? 'log(1 + Ingreso en Bs)' : 'Ingreso Operativo Anual (Bs)'
        },
        yaxis: {
          ...state.plotlyLayoutBase.yaxis,
          title: 'Número de Empresas'
        },
        margin: { l: 60, r: 30, t: 50, b: 60 }
      };

      Plotly.newPlot('chartDistribution', [trace], layout, { responsive: true, displayModeBar: false });
    } catch (e) {
      console.error('Error al graficar distribución:', e);
    }
  }

  async function renderBoxplotDeptos() {
    try {
      const res = await fetch('/api/eda/boxplot_deptos');
      const data = await res.json();

      const traces = data.map(d => ({
        y: d.sample_log,
        type: 'box',
        name: d.depto,
        boxpoints: 'outliers',
        marker: { size: 4 }
      }));

      const layout = {
        ...state.plotlyLayoutBase,
        title: 'Ingresos por Departamento (Escala log)',
        yaxis: { ...state.plotlyLayoutBase.yaxis, title: 'log(1 + Ingreso Bs)' },
        showlegend: false,
        margin: { l: 50, r: 20, t: 40, b: 60 }
      };

      Plotly.newPlot('chartBoxDeptos', traces, layout, { responsive: true, displayModeBar: false });
    } catch (e) {
      console.error('Error al graficar boxplot departamentos:', e);
    }
  }

  async function renderBoxplotSectors() {
    try {
      const res = await fetch('/api/eda/boxplot_sectors');
      const data = await res.json();

      const traces = data.slice(0, 6).map(s => ({
        y: s.sample_log,
        type: 'box',
        name: s.sector.length > 18 ? s.sector.substring(0, 16) + '...' : s.sector,
        boxpoints: 'outliers',
        marker: { size: 4 }
      }));

      const layout = {
        ...state.plotlyLayoutBase,
        title: 'Ingresos por Macrosector Económico',
        yaxis: { ...state.plotlyLayoutBase.yaxis, title: 'log(1 + Ingreso Bs)' },
        showlegend: false,
        margin: { l: 50, r: 20, t: 40, b: 80 }
      };

      Plotly.newPlot('chartBoxSectors', traces, layout, { responsive: true, displayModeBar: false });
    } catch (e) {
      console.error('Error al graficar boxplot sectores:', e);
    }
  }

  async function renderCorrelationChart() {
    try {
      const res = await fetch('/api/eda/correlations');
      const data = await res.json();

      const trace = {
        z: data.matrix,
        x: data.labels,
        y: data.labels,
        type: 'heatmap',
        colorscale: [
          [0, '#f0edef'],
          [0.5, '#6bd8cb'],
          [1, '#004b44']
        ],
        showscale: true
      };

      const layout = {
        ...state.plotlyLayoutBase,
        margin: { l: 120, r: 30, t: 30, b: 110 },
        xaxis: { tickangle: -45, ...state.plotlyLayoutBase.xaxis },
        yaxis: { ...state.plotlyLayoutBase.yaxis }
      };

      Plotly.newPlot('chartCorrelation', [trace], layout, { responsive: true, displayModeBar: false });
    } catch (e) {
      console.error('Error al graficar correlación:', e);
    }
  }

  async function renderOutliersChart() {
    try {
      const res = await fetch('/api/eda/outliers');
      const data = await res.json();

      const normalPoints = data.points.filter(p => !p.is_outlier);
      const outlierPoints = data.points.filter(p => p.is_outlier);

      const traceNormal = {
        x: normalPoints.map(p => Math.log1p(p.sueldos_bs)),
        y: normalPoints.map(p => Math.log1p(p.ingreso_bs)),
        mode: 'markers',
        type: 'scatter',
        name: 'Regulares',
        marker: { color: '#006a61', size: 6, opacity: 0.7 }
      };

      const traceOutlier = {
        x: outlierPoints.map(p => Math.log1p(p.sueldos_bs)),
        y: outlierPoints.map(p => Math.log1p(p.ingreso_bs)),
        mode: 'markers',
        type: 'scatter',
        name: 'Atípicos (IQR)',
        marker: { color: '#ba1a1a', size: 8, symbol: 'diamond' }
      };

      const layout = {
        ...state.plotlyLayoutBase,
        title: 'Sueldos vs. Ingresos (Auditoría de Consistencia)',
        xaxis: { ...state.plotlyLayoutBase.xaxis, title: 'log(1 + Sueldos Básicos Bs)' },
        yaxis: { ...state.plotlyLayoutBase.yaxis, title: 'log(1 + Ingreso Bs)' },
        margin: { l: 60, r: 20, t: 40, b: 60 }
      };

      Plotly.newPlot('chartOutliers', [traceNormal, traceOutlier], layout, { responsive: true, displayModeBar: false });
    } catch (e) {
      console.error('Error al graficar outliers:', e);
    }
  }

  // --------------------------------------------------------------------------
  // 6. SECCIÓN 4: PREPROCESAMIENTO Y PIPELINE
  // --------------------------------------------------------------------------
  async function loadPipeline() {
    const container = document.getElementById('pipelineStepper');
    try {
      const res = await fetch('/api/pipeline');
      const data = await res.json();

      container.innerHTML = data.steps.map(s => `
        <div class="step-card">
          <div class="step-num">${s.step}</div>
          <div class="step-content">
            <h4>${s.title}</h4>
            <p>${s.desc}</p>
          </div>
        </div>
      `).join('');
    } catch (e) {
      console.error('Error al cargar pipeline:', e);
    }
  }

  // --------------------------------------------------------------------------
  // 7. SECCIÓN 5: MODELADO Y RESULTADOS
  // --------------------------------------------------------------------------
  async function renderModeladoPanel() {
    try {
      if (!state.modelsData) {
        const res = await fetch('/api/models');
        state.modelsData = await res.json();
      }

      const m = state.modelsData.metrics_comparison;
      const tableBody = document.getElementById('modelsTableBody');

      if (m && Object.keys(m).length > 0) {
        tableBody.innerHTML = Object.keys(m).map(name => {
          const item = m[name];
          const isBest = name === state.modelsData.active_model;
          return `
            <tr style="${isBest ? 'background-color: var(--primary-light); font-weight:600;' : ''}">
              <td><strong>${name}</strong></td>
              <td>${item.cv_r2_mean.toFixed(4)}</td>
              <td>${item.r2_log.toFixed(4)}</td>
              <td style="color: ${item.r2_bs >= 0.70 ? 'var(--accent-emerald)' : 'inherit'}; font-weight:700;">
                ${item.r2_bs.toFixed(4)}
              </td>
              <td>Bs ${Math.round(item.mae_bs).toLocaleString('es-BO')}</td>
              <td>${item.medape_percent.toFixed(2)}%</td>
              <td>
                <span class="status-pill-subtle ${isBest ? 'active' : 'archived'}">
                  ${isBest ? 'En Producción' : 'Evaluado'}
                </span>
              </td>
            </tr>
          `;
        }).join('');
      }

      // Gráficos de diagnóstico
      const diag = state.modelsData.test_diagnostics;
      if (diag && diag.real_log) {
        // Real vs Predicho
        const traceScatter = {
          x: diag.real_log,
          y: diag.pred_log,
          mode: 'markers',
          type: 'scatter',
          name: 'Predicciones',
          marker: { color: '#006a61', size: 6, opacity: 0.65 }
        };
        const minVal = Math.min(...diag.real_log);
        const maxVal = Math.max(...diag.real_log);
        const traceLine = {
          x: [minVal, maxVal],
          y: [minVal, maxVal],
          mode: 'lines',
          type: 'scatter',
          name: 'Ideal (y = x)',
          line: { color: '#ba1a1a', dash: 'dash', width: 2 }
        };

        const layoutScatter = {
          ...state.plotlyLayoutBase,
          title: 'Valores Reales vs. Predichos (Log)',
          xaxis: { ...state.plotlyLayoutBase.xaxis, title: 'Valor Real log(1 + Bs)' },
          yaxis: { ...state.plotlyLayoutBase.yaxis, title: 'Valor Predicho log(1 + Bs)' },
          margin: { l: 50, r: 20, t: 40, b: 50 }
        };
        Plotly.newPlot('chartRealVsPred', [traceScatter, traceLine], layoutScatter, { responsive: true, displayModeBar: false });

        // Gráfico de Residuos
        const traceRes = {
          x: diag.pred_log,
          y: diag.residuals_log,
          mode: 'markers',
          type: 'scatter',
          name: 'Residuo',
          marker: { color: '#f97316', size: 6, opacity: 0.7 }
        };
        const traceZero = {
          x: [minVal, maxVal],
          y: [0, 0],
          mode: 'lines',
          line: { color: '#76777d', dash: 'dot', width: 1.5 }
        };

        const layoutRes = {
          ...state.plotlyLayoutBase,
          title: 'Residuos vs. Predicción',
          xaxis: { ...state.plotlyLayoutBase.xaxis, title: 'Predicción log(1 + Bs)' },
          yaxis: { ...state.plotlyLayoutBase.yaxis, title: 'Residuo (Real - Predicho)' },
          showlegend: false,
          margin: { l: 50, r: 20, t: 40, b: 50 }
        };
        Plotly.newPlot('chartResiduals', [traceRes, traceZero], layoutRes, { responsive: true, displayModeBar: false });
      }

      // Feature Importance
      const fi = state.modelsData.feature_importance;
      if (fi && fi.length > 0) {
        const sortedFi = [...fi].reverse();
        const traceFi = {
          x: sortedFi.map(f => f.importance),
          y: sortedFi.map(f => f.feature.replace('log_', '').replace('cat__', '')),
          type: 'bar',
          orientation: 'h',
          marker: { color: '#006a61' }
        };

        const layoutFi = {
          ...state.plotlyLayoutBase,
          title: 'Importancia Relativa de Predictores (Gini)',
          xaxis: { ...state.plotlyLayoutBase.xaxis, title: 'Peso Relativo' },
          margin: { l: 140, r: 30, t: 40, b: 50 }
        };
        Plotly.newPlot('chartFeatureImportance', [traceFi], layoutFi, { responsive: true, displayModeBar: false });
      }
    } catch (e) {
      console.error('Error al renderizar resultados de modelos:', e);
    }
  }

  // --------------------------------------------------------------------------
  // 8. SECCIÓN 6: PREDICCIÓN INTERACTIVA
  // --------------------------------------------------------------------------
  const predictionForm = document.getElementById('predictionForm');
  const resultCard = document.getElementById('predictionResultCard');
  const resultAmount = document.getElementById('resultPredictionAmount');
  const resultInterval = document.getElementById('resultInterval');
  const resultCategory = document.getElementById('resultSizeCategory');

  predictionForm.addEventListener('submit', async (e) => {
    e.preventDefault();

    const payload = {
      depto: document.getElementById('predDepto').value,
      sector_macro: document.getElementById('predSector').value,
      personal: parseFloat(document.getElementById('predPersonal').value) || 0,
      sueldos: parseFloat(document.getElementById('predSueldos').value) || 0,
      remuneraciones: parseFloat(document.getElementById('predRemuneraciones').value) || 0,
      energia: parseFloat(document.getElementById('predEnergia').value) || 0,
      activos: parseFloat(document.getElementById('predActivos').value) || 0,
      inventarios: parseFloat(document.getElementById('predInventarios').value) || 0,
      total_valor_co: parseFloat(document.getElementById('predInsumosCompras').value) || 0,
      total_valor_uti: parseFloat(document.getElementById('predInsumosUtil').value) || 0,
      n_insumos: parseInt(document.getElementById('predNInsumos').value) || 0,
      capacidad_mp: parseFloat(document.getElementById('predCapacidadMP').value) || 0,
      capacidad_pt: 0
    };

    resultAmount.textContent = 'Calculando...';

    try {
      const res = await fetch('/api/predict', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload)
      });
      const data = await res.json();

      if (data.success) {
        resultCard.classList.add('has-result');
        resultAmount.textContent = data.prediction_formatted;
        resultInterval.textContent = data.interval_formatted;

        resultCategory.textContent = data.categoria_tamano;
        resultCategory.className = `size-category-badge ${data.categoria_color}`;
      } else {
        resultAmount.textContent = 'Error';
        alert('Error en la predicción: ' + (data.error || 'Desconocido'));
      }
    } catch (err) {
      console.error('Error al predecir:', err);
      resultAmount.textContent = 'Error de conexión';
    }
  });

  // --------------------------------------------------------------------------
  // 9. SECCIÓN 7: MLOPS Y MONITOREO
  // --------------------------------------------------------------------------
  async function loadMLOps() {
    try {
      const res = await fetch('/api/mlops');
      const data = await res.json();

      document.getElementById('mlopsActiveVersion').textContent = data.active_version;
      document.getElementById('mlopsLastUpdated').textContent = new Date(data.last_updated).toLocaleString('es-BO');

      // Trazabilidad de versiones
      const tbody = document.getElementById('mlopsHistoryTableBody');
      if (data.history && data.history.length > 0) {
        tbody.innerHTML = data.history.map(item => `
          <tr>
            <td><strong class="font-mono">${item.version}</strong></td>
            <td>${item.model_type}</td>
            <td>${new Date(item.timestamp).toLocaleString('es-BO')}</td>
            <td>${item.dataset_rows}</td>
            <td style="color: var(--accent-emerald); font-weight:600;">${item.metrics.r2_bs.toFixed(4)}</td>
            <td>${item.metrics.medape_percent.toFixed(2)}%</td>
            <td>
              <span class="status-pill-subtle ${item.status === 'ACTIVE' ? 'active' : 'archived'}">
                ${item.status === 'ACTIVE' ? 'Activo' : 'Archivado'}
              </span>
            </td>
          </tr>
        `).join('');
      }

      // Render Drift List
      renderDriftList(data.drift_metrics);
    } catch (e) {
      console.error('Error al cargar MLOps:', e);
    }
  }

  function renderDriftList(driftData) {
    const list = document.getElementById('driftStatusList');
    if (!driftData) return;

    list.innerHTML = Object.keys(driftData).map(key => {
      const item = driftData[key];
      const isDrift = item.drift_detected;
      return `
        <div style="display: flex; justify-content: space-between; align-items: center; border-bottom: 1px solid var(--border-color); padding-bottom: 0.4rem;">
          <div>
            <div style="font-weight: 600; font-size: 0.85rem;">${item.label}</div>
            <div style="font-size: 0.72rem; color: var(--text-muted);">
              KS Stat: ${item.ks_stat} | p-value: ${item.p_value}
            </div>
          </div>
          <span class="status-pill-subtle ${isDrift ? 'danger' : 'active'}">
            ${item.status}
          </span>
        </div>
      `;
    }).join('');
  }

  const btnTestDrift = document.getElementById('btnTestDrift');
  btnTestDrift.addEventListener('click', async () => {
    try {
      btnTestDrift.textContent = 'Evaluando...';
      const res = await fetch('/api/mlops/drift', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ feature: 'S02_09' }) // Simular drift en energía
      });
      const data = await res.json();
      renderDriftList(data.drift_results);
      btnTestDrift.textContent = 'Simular Prueba KS';
    } catch (e) {
      console.error('Error al simular drift:', e);
      btnTestDrift.textContent = 'Simular Prueba KS';
    }
  });

});
