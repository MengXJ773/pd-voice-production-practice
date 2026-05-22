<template>
  <div>
    <p>请在下方输入您的姓名，并选择需要上传的音频文件（wav或mp3格式），建议为朗读一段文本的录音。上传完成后，您将在下方看到预测结果,结果为是则代表有较大可能患有帕金森，否则相反。
      系统不是百分百准确，建议可以使用不同的录音多次预测并比对结果。系统结果仅作参考，更准确结果可以向医生确认。</p>
    <input type="text" v-model="userName" placeholder="请输入用户姓名" />
    <input type="file" @change="handleFileUpload" />
    <button @click="submitFile">上传文件</button>
    <div v-if="uploadResult">
      预测结果: {{ uploadResult.prediction }}
    </div>
    <button @click="fetchHistory">获取历史记录</button>
    <div class="history-section">
      <h3>历史记录</h3>
      <p>以下是过去上传的文件的历史记录及其预测结果：</p>
      <ul>
        <li v-for="(record, index) in histories" :key="index">
          用户名: {{ record.user_name }}, 上传时间: {{ record.upload_time }}, 预测结果: {{ record.prediction }}
        </li>
      </ul>
    </div>
  </div>
</template>



<script>
import axios from 'axios';
const API_BASE_URL = process.env.VUE_APP_API_BASE_URL || 'http://127.0.0.1:5000';

export default {
  data() {
    return {
      userName: '',
      selectedFile: null,
      uploadResult: null,
      histories: [],
    };
  },

  methods: {
    handleFileUpload(event) {
      this.selectedFile = event.target.files[0];
    },
    submitFile() {
      const formData = new FormData();
      formData.append('file', this.selectedFile);
      formData.append('userName', this.userName);

      axios.post(`${API_BASE_URL}/upload`, formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      })
      .then(response => {
        this.uploadResult = response.data;
      })
      .catch(error => {
        console.error("There was an error uploading the file", error);
      });
    },
    fetchHistory() {
      axios.get(`${API_BASE_URL}/history`)
        .then(response => {
          this.histories = response.data;  // 假设histories是绑定到模板的一个数组
        })
        .catch(error => {
          console.error("There was an error fetching the history", error);
        });
    },
  },
};
</script>

<style scoped>
/* 整体布局样式 */
div {
  display: flex;
  flex-direction: column;
  align-items: center;
  margin-top: 20px;
}

/*字体样式 */
p {
  font-size: 16px;
  color: #333;
  margin: 10px 0;
}

/* 输入框样式 */
input[type="text"], input[type="file"] {
  margin: 10px 0;
  padding: 8px;
  border: 1px solid #ccc;
  border-radius: 4px;
  width: 300px; /* 可根据需要调整宽度 */
}

/* 按钮样式 */
button {
  background-color: #4CAF50;
  color: white;
  padding: 10px 20px;
  margin: 10px 0;
  border: none;
  border-radius: 4px;
  cursor: pointer;
}

button:hover {
  background-color: #45a049;
}

/* 预测结果样式 */
.uploadResult {
  margin: 20px 0;
  padding: 10px;
  background-color: #f2f2f2;
  border-left: 5px solid #4CAF50;
  border-radius: 4px;
}

/* 历史记录区域样式 */
.history-section {
  margin-top: 20px;
  width: 80%;
}

.history-section h3 {
  margin-bottom: 10px;
}

ul {
  list-style-type: none;
  padding: 0;
}

li {
  margin: 5px 0;
  padding: 10px;
  background-color: #f9f9f9;
  border: 1px solid #ddd;
  border-radius: 4px;
}
</style>
