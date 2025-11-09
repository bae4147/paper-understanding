# ACM Paper 추출 북마클릿

## 사용 방법

1. 아래 북마클릿 코드를 복사
2. 브라우저 북마크 바에 새 북마크 생성
3. URL 부분에 코드 붙여넣기
4. ACM 논문 페이지에서 북마크 클릭
5. 정리된 HTML 다운로드

## 북마클릿 코드

```javascript
javascript:(function(){
  // Extract paper content from ACM Digital Library
  const content = [];
  
  // Title
  const title = document.querySelector('h1.citation__title');
  if (title) content.push(`<h1 class="text-4xl font-bold mb-4">${title.textContent.trim()}</h1>`);
  
  // Authors
  const authors = Array.from(document.querySelectorAll('.authors-section .author-name'))
    .map(a => a.textContent.trim()).join(', ');
  if (authors) content.push(`<p class="text-gray-600 mb-8">${authors}</p>`);
  
  // Abstract
  const abstract = document.querySelector('.abstractSection p');
  if (abstract) {
    content.push('<h2 class="text-2xl font-bold mb-4 mt-8">Abstract</h2>');
    content.push(`<p class="mb-4 text-justify">${abstract.textContent.trim()}</p>`);
  }
  
  // Main content
  const mainContent = document.querySelector('.article__body') || document.querySelector('.hlFld-Fulltext');
  if (mainContent) {
    mainContent.querySelectorAll('h2, h3, p, figure').forEach(el => {
      if (el.tagName === 'H2') {
        content.push(`<h2 class="text-2xl font-bold mb-4 mt-8">${el.textContent.trim()}</h2>`);
      } else if (el.tagName === 'H3') {
        content.push(`<h3 class="text-xl font-bold mb-3 mt-6">${el.textContent.trim()}</h3>`);
      } else if (el.tagName === 'P' && el.textContent.trim().length > 20) {
        content.push(`<p class="mb-4 text-justify">${el.textContent.trim()}</p>`);
      } else if (el.tagName === 'FIGURE') {
        const img = el.querySelector('img');
        const caption = el.querySelector('figcaption');
        if (img) {
          content.push(`<div class="my-8"><img src="${img.src}" class="max-w-full mx-auto shadow-lg rounded" />`);
          if (caption) content.push(`<p class="text-sm text-gray-600 text-center mt-2 italic">${caption.textContent.trim()}</p>`);
          content.push('</div>');
        }
      }
    });
  }
  
  // Generate HTML
  const html = `<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>${title ? title.textContent.trim() : 'ACM Paper'}</title>
    <script src="https://cdn.tailwindcss.com"></script>
</head>
<body class="bg-gray-50 p-8">
    <div class="max-w-4xl mx-auto bg-white shadow-xl rounded-lg p-12">
        <div class="prose max-w-none">
            ${content.join('\n')}
        </div>
    </div>
</body>
</html>`;
  
  // Download
  const blob = new Blob([html], {type: 'text/html'});
  const url = URL.createObjectURL(blob);
  const a = document.createElement('a');
  a.href = url;
  a.download = 'paper.html';
  a.click();
  URL.revokeObjectURL(url);
  alert('Paper HTML downloaded!');
})();
```

## 한 줄 버전 (북마크에 넣기)

```
javascript:(function(){const content=[];const title=document.querySelector('h1.citation__title');if(title)content.push(`<h1 class="text-4xl font-bold mb-4">${title.textContent.trim()}</h1>`);const authors=Array.from(document.querySelectorAll('.authors-section .author-name')).map(a=>a.textContent.trim()).join(', ');if(authors)content.push(`<p class="text-gray-600 mb-8">${authors}</p>`);const abstract=document.querySelector('.abstractSection p');if(abstract){content.push('<h2 class="text-2xl font-bold mb-4 mt-8">Abstract</h2>');content.push(`<p class="mb-4 text-justify">${abstract.textContent.trim()}</p>`);}const mainContent=document.querySelector('.article__body')||document.querySelector('.hlFld-Fulltext');if(mainContent){mainContent.querySelectorAll('h2, h3, p, figure').forEach(el=>{if(el.tagName==='H2'){content.push(`<h2 class="text-2xl font-bold mb-4 mt-8">${el.textContent.trim()}</h2>`);}else if(el.tagName==='H3'){content.push(`<h3 class="text-xl font-bold mb-3 mt-6">${el.textContent.trim()}</h3>`);}else if(el.tagName==='P'&&el.textContent.trim().length>20){content.push(`<p class="mb-4 text-justify">${el.textContent.trim()}</p>`);}else if(el.tagName==='FIGURE'){const img=el.querySelector('img');const caption=el.querySelector('figcaption');if(img){content.push(`<div class="my-8"><img src="${img.src}" class="max-w-full mx-auto shadow-lg rounded" />`);if(caption)content.push(`<p class="text-sm text-gray-600 text-center mt-2 italic">${caption.textContent.trim()}</p>`);content.push('</div>');}}});}const html=`<!DOCTYPE html><html lang="en"><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1.0"><title>${title?title.textContent.trim():'ACM Paper'}</title><script src="https://cdn.tailwindcss.com"></script></head><body class="bg-gray-50 p-8"><div class="max-w-4xl mx-auto bg-white shadow-xl rounded-lg p-12"><div class="prose max-w-none">${content.join('\n')}</div></div></body></html>`;const blob=new Blob([html],{type:'text/html'});const url=URL.createObjectURL(blob);const a=document.createElement('a');a.href=url;a.download='paper.html';a.click();URL.revokeObjectURL(url);alert('Paper HTML downloaded!');})();
```

## 또 다른 간단한 방법

브라우저 확장 프로그램 없이:

1. ACM 페이지 열기
2. F12 (개발자 도구)
3. Console 탭
4. 위의 자바스크립트 코드 붙여넣기
5. Enter
6. paper.html 자동 다운로드!
