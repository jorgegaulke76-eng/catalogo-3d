<!DOCTYPE html>
<html lang="pt-br">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Alphafest Itatiba | Personalização e Impressão 3D</title>
    <style>
        :root { 
            --primary-color: #27ae60; 
            --dark: #333; 
            --light-gray: #f4f4f4;
            --white: #ffffff;
        }

        * { box-sizing: border-box; }

        body { 
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; 
            background-color: var(--light-gray); 
            margin: 0; 
            color: var(--dark);
            line-height: 1.6;
        }
        
        .hero { 
            background: var(--white); 
            padding: 60px 20px; 
            text-align: center; 
            border-bottom: 3px solid var(--primary-color);
        }

        .hero h1 { 
            margin: 0 0 10px 0; 
            color: var(--dark); 
            font-size: 2.5em;
        }

        .hero p { 
            color: #666; 
            margin-bottom: 25px;
            font-size: 1.1em;
        }

        nav { 
            background: var(--dark); 
            padding: 15px; 
            position: sticky; 
            top: 0; 
            z-index: 1000; 
            display: flex; 
            gap: 30px; 
            justify-content: center; 
            box-shadow: 0 2px 5px rgba(0,0,0,0.1);
        }

        nav a { 
            color: var(--white); 
            text-decoration: none; 
            font-weight: 600; 
            transition: color 0.3s;
        }

        nav a:hover { color: var(--primary-color); }

        .container { 
            max-width: 1000px; 
            margin: 40px auto; 
            padding: 0 20px; 
        }

        h2 { text-align: center; margin-bottom: 40px; color: var(--dark); }

        .grid { 
            display: grid; 
            grid-template-columns: repeat(auto-fill, minmax(280px, 1fr)); 
            gap: 30px; 
        }
        
        .card { 
            background: var(--white); 
            border-radius: 12px; 
            padding: 20px; 
            transition: transform 0.3s ease, box-shadow 0.3s ease; 
            box-shadow: 0 4px 10px rgba(0,0,0,0.05); 
        }

        .card:hover { 
            transform: translateY(-10px); 
            box-shadow: 0 10px 20px rgba(0,0,0,0.1); 
        }

        .card img { 
            width: 100%; 
            height: 220px; 
            object-fit: cover; 
            border-radius: 8px; 
            margin-bottom: 15px;
        }
        
        .card h3 { margin: 10px 0; }

        .preco { 
            color: var(--primary-color); 
            font-size: 1.4em; 
            font-weight: bold; 
            margin: 10px 0; 
            display: block; 
        }
        
        .btn-whats { 
            display: inline-block; 
            background-color: var(--primary-color); 
            color: var(--white); 
            padding: 15px 30px; 
            text-decoration: none; 
            border-radius: 50px; 
            font-weight: bold; 
            transition: background 0.3s;
        }

        .btn-whats:hover { background-color: #219150; }
    </style>
</head>
<body>

    <header class="hero">
        <h1>Alphafest Itatiba</h1>
        <p>Soluções em impressão 3D, gravação a laser e brindes personalizados.</p>
        <a href="https://wa.me/SEUNUMERO" class="btn-whats">Falar no WhatsApp</a>
    </header>

    <nav>
        <a href="#produtos">Produtos</a>
        <a href="#sobre">Sobre</a>
        <a href="#contato">Contato</a>
    </nav>

    <div class="container" id="produtos">
        <h2>Nossos Destaques</h2>
        <div class="grid">
            <!-- Exemplo de Produto -->
            <div class="card">
                <img src="https://via.placeholder.com/300x200" alt="Copo Térmico Personalizado">
                <h3>Copo Térmico Personalizado</h3>
                <span class="preco">R$ 89,90</span>
                <p>Gravação a laser com alta precisão.</p>
            </div>
            <!-- Duplique este bloco para mais produtos -->
        </div>
    </div>

</body>
</html>
