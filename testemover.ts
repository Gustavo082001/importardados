<!DOCTYPE html>
<html lang="pt-br">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Visualizador e Editor de PDF</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            margin: 20px;
        }
        #pdf-container {
            position: relative;
            border: 1px solid #ccc;
            width: 100%;
            max-width: 800px;
            height: 600px;
            overflow: auto;
        }
        #pdf-render {
            width: 100%;
        }
        .draggable-text {
            position: absolute;
            cursor: move;
            background-color: rgba(255, 255, 0, 0.7);
            padding: 5px;
            border: 1px solid #000;
            user-select: none;
        }
        #controls {
            margin-bottom: 10px;
        }
        #coordinates {
            margin-top: 10px;
            font-weight: bold;
        }
    </style>
</head>
<body>
    <h1>Visualizador e Editor de PDF</h1>
    <div id="controls">
        <input type="file" id="file-input" accept="application/pdf">
        <button id="add-text-btn">Adicionar Texto</button>
        <div id="coordinates">Coordenadas: X: 0, Y: 0</div>
    </div>
    <div id="pdf-container">
        <canvas id="pdf-render"></canvas>
    </div>

    <!-- Inclui a biblioteca PDF.js -->
    <script src="https://mozilla.github.io/pdf.js/build/pdf.js"></script>
    <script>
        const fileInput = document.getElementById('file-input');
        const addTextBtn = document.getElementById('add-text-btn');
        const pdfContainer = document.getElementById('pdf-container');
        const pdfRender = document.getElementById('pdf-render');
        const coordinatesDiv = document.getElementById('coordinates');

        let pdfDoc = null;
        let pageNum = 1;
        let scale = 1.0;

        // Configura o worker do PDF.js
        pdfjsLib.GlobalWorkerOptions.workerSrc = 'https://mozilla.github.io/pdf.js/build/pdf.worker.js';

        // Carrega e renderiza o PDF selecionado
        fileInput.addEventListener('change', (e) => {
            const file = e.target.files[0];
            if (file && file.type === 'application/pdf') {
                const fileReader = new FileReader();
                fileReader.onload = function() {
                    const typedArray = new Uint8Array(this.result);
                    pdfjsLib.getDocument(typedArray).promise.then((pdf) => {
                        pdfDoc = pdf;
                        renderPage(pageNum);
                    });
                };
                fileReader.readAsArrayBuffer(file);
            }
        });

        function renderPage(num) {
            pdfDoc.getPage(num).then((page) => {
                const viewport = page.getViewport({ scale });
                pdfRender.height = viewport.height;
                pdfRender.width = viewport.width;

                const ctx = pdfRender.getContext('2d');
                ctx.clearRect(0, 0, pdfRender.width, pdfRender.height);

                const renderContext = {
                    canvasContext: ctx,
                    viewport: viewport
                };
                page.render(renderContext);
            });
        }

        // Adiciona texto ao PDF
        addTextBtn.addEventListener('click', () => {
            const text = document.createElement('div');
            text.classList.add('draggable-text');
            text.textContent = 'Texto Editável';
            text.style.left = '50px';
            text.style.top = '50px';
            pdfContainer.appendChild(text);
            makeDraggable(text);
        });

        function makeDraggable(element) {
            let offsetX = 0, offsetY = 0, isDragging = false;

            element.addEventListener('mousedown', (e) => {
                isDragging = true;
                offsetX = e.clientX - element.offsetLeft;
                offsetY = e.clientY - element.offsetTop;
            });

            document.addEventListener('mousemove', (e) => {
                if (isDragging) {
                    const x = e.clientX - offsetX;
                    const y = e.clientY - offsetY;
                    element.style.left = `${x}px`;
                    element.style.top = `${y}px`;
                    coordinatesDiv.textContent = `Coordenadas: X: ${x}, Y: ${y}`;
                }
            });

            document.addEventListener('mouseup', () => {
                isDragging = false;
            });
        }
    </script>
</body>
</html>
