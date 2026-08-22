<script>
            let db = {datos_json};
            let tabActual = Object.keys(db)[0];

            function construirTabs() {{
                let html = "";
                for (let clave in db) {{
                    html += `<button class="tab-btn ${{clave === tabActual ? 'active' : ''}}" onclick="cambiarTab('${{clave}}')">${{db[clave].nombre}}</button>`;
                }}
                document.getElementById('contenedor_tabs').innerHTML = html;
            }}

            function cambiarTab(clave) {{ tabActual = clave; construirTabs(); actualizarVista(); }}

            function actualizarVista() {{
                let info = db[tabActual];
                document.getElementById('titulo_sala').innerText = "📊 TRABAJO DE IA: " + info.nombre.toUpperCase();
                let html = "";
                
                if (info.tipo_juego === 'quiniela' && info.rankings) {{
                    html += "<h3>⭐ TOP 5 NÚMEROS:</h3><table><tr><th>#</th><th>Número</th><th>Fuerza</th></tr>";
                    info.rankings.top5_nums.forEach((n, i) => {{ 
                        html += `<tr><td>#${{i+1}}</td><td style="color:#38bdf8; font-weight:bold; font-size:15px;">${{n.num}}</td><td style="color:#4ade80;">${{n.fuerza}}%</td></tr>`; 
                    }});
                    html += "</table><h3>💥 TOP 5 PALÉS MAESTROS:</h3>";
                    info.rankings.top5_pales.forEach((p, i) => {{ 
                        html += `<p style="margin:6px 0; font-size:13px; display:flex; justify-content:space-between; align-items:center;"><span>#${{i+1}}: <b style="color:#facc15; font-size:14px;">${{p.pale}}</b></span> <span style="color:#4ade80; font-weight:bold;">${{p.fuerza}}%</span></p>`; 
                    }});
                    html += "<h3>🏆 TRIPLETA RECOMENDADA:</h3><p style='font-size:15px; color:#f472b6; font-weight:bold;'>[${{info.rankings.top5_tripletas[0]}}]</p>";
                    html += "<h3>📊 TOP 20 GENERAL (COBERTURA):</h3><div style='max-height:180px; overflow-y:auto; border:1px solid #1e293b; border-radius:6px;'><table>";
                    info.rankings.top20.forEach((n, i) => {{ 
                        html += `<tr><td>#${{i+1}}</td><td>${{n.num}}</td><td>${{n.fuerza}}%</td></tr>`; 
                    }});
                    html += "</table></div>";
                }} 
                // ... (resto de las condiciones kino, primitiva, euromillon igual)
                else if (info.tipo_juego === 'kino') {{
                    html += "<h3>👑 JUGADA A:</h3><div style='text-align:center; margin:10px 0;'>";
                    info.kino_data.jugada_a.forEach(d => {{ html += `<span class='ball'>${{d}}</span>`; }});
                    html += "</div><h3>👑 JUGADA B:</h3><div style='text-align:center; margin:10px 0;'>";
                    info.kino_data.jugada_b.forEach(d => {{ html += `<span class='ball'>${{d}}</span>`; }});
                    html += "</div>";
                }}
                else if (info.tipo_juego === 'primitiva') {{
                    html += `<p style="color:#facc15; font-weight:bold;">🇪🇸 Reintegro: <span style="font-size:18px; color:#fff;">${{info.primitiva_data.reintegro}}</span></p><h3>🇪🇸 MATRIZ PRIMITIVA:</h3><div style='text-align:center; margin:15px 0;'>`;
                    info.primitiva_data.numeros_base.forEach(n => {{ html += `<span class='ball'>${{n}}</span>`; }});
                    html += "</div>";
                }}
                else if (info.tipo_juego === 'euromillones') {{
                    html += "<h3>🇪🇺 ESTRELLAS:</h3><div style='text-align:center; margin:10px 0;'>";
                    info.euro_data.estrellas.forEach(e => {{ html += `<span class='ball' style='background:#38bdf8; color:#0f172a;'>⭐${{e}}</span>`; }});
                    html += "</div><h3>🇪🇺 NÚMEROS:</h3><div style='text-align:center; margin:15px 0;'>";
                    info.euro_data.numeros.forEach(n => {{ html += `<span class='ball'>${{n}}</span>`; }});
                    html += "</div>";
                }}
                
                document.getElementById('contenido_sala').innerHTML = html;
            }}

            // NUEVA FUNCIÓN: Auto-refresco cada 60 segundos
            setInterval(() => {{
                location.reload();
            }}, 60000); 

            construirTabs(); 
            actualizarVista();
        </script>
