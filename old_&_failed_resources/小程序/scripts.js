document.addEventListener('DOMContentLoaded', function () {
    const userNameInput = document.getElementById('userName');
    const fileInput = document.getElementById('fileInput');
    const uploadButton = document.getElementById('uploadButton');
    const uploadResultDiv = document.getElementById('uploadResult');
    const predictionSpan = document.getElementById('prediction');
    const fetchHistoryButton = document.getElementById('fetchHistoryButton');
    const historySection = document.getElementById('historySection');
    const historyList = document.getElementById('historyList');

    uploadButton.addEventListener('click', function () {
        const userName = userNameInput.value;
        const file = fileInput.files[0];

        if (!userName || !file) {
            alert('请填写姓名并选择文件');
            return;
        }

        const formData = new FormData();
        formData.append('file', file);
        formData.append('userName', userName);

        fetch('https://your-server.com/upload', {
            method: 'POST',
            body: formData,
        })
        .then(response => response.json())
        .then(data => {
            predictionSpan.textContent = data.prediction;
            uploadResultDiv.style.display = 'block';
        })
        .catch(error => {
            console.error('Error uploading file:', error);
        });
    });

    fetchHistoryButton.addEventListener('click', function () {
        fetch('https://your-server.com/history')
        .then(response => response.json())
        .then(data => {
            historyList.innerHTML = '';
            data.forEach(record => {
                const listItem = document.createElement('li');
                listItem.textContent = `用户名: ${record.user_name}, 上传时间: ${record.upload_time}, 预测结果: ${record.prediction}`;
                historyList.appendChild(listItem);
            });
            historySection.style.display = 'block';
        })
        .catch(error => {
            console.error('Error fetching history:', error);
        });
    });
});
