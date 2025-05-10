document.addEventListener('DOMContentLoaded', function() {
    const slangDictionary = {};

    document.getElementById('add-slang-button').addEventListener('click', function() {
        const originalWord = document.getElementById('original-word').value.trim();
        const replacementWord = document.getElementById('replacement-word').value.trim();

        if (originalWord && replacementWord) {
            if (slangDictionary.hasOwnProperty(originalWord)) {
                alert(`"${originalWord}" is already in the slang dictionary.`);
            } else {
                slangDictionary[originalWord] = replacementWord;
                updateSlangDictionary();
                alert(`Slang word "${originalWord}" added successfully!`);
            }

            // Clear inputs
            document.getElementById('original-word').value = '';
            document.getElementById('replacement-word').value = '';
        }
    });

    function updateSlangDictionary() {
        const slangList = document.getElementById('slang-dictionary');
        slangList.innerHTML = '';

        for (const [slang, replacement] of Object.entries(slangDictionary)) {
            slangList.innerHTML += `<li><strong>${slang}</strong> ➔ ${replacement}</li>`;
        }
    }

    document.getElementById('download-slang-button').addEventListener('click', function() {
        const dataStr = "data:text/json;charset=utf-8," + encodeURIComponent(JSON.stringify(slangDictionary, null, 2));
        const downloadAnchor = document.createElement('a');
        downloadAnchor.setAttribute("href", dataStr);
        downloadAnchor.setAttribute("download", "custom_slang_dictionary.json");
        document.body.appendChild(downloadAnchor);
        downloadAnchor.click();
        document.body.removeChild(downloadAnchor);
    });
    
});
