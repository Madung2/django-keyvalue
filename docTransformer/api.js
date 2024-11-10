const formData = new FormData();

// 예시 파일 객체 생성 (실제 시 file1, file2, file3는 유효한 File 객체여야 함)
const file1 = new File(["content1"], "file1.pdf");
const file2 = new File(["content2"], "file2.pdf");
const file3 = new File(["content3"], "file3.pdf");

// 각 파일과 파일 이름을 추가
const files = [
  { file: file1, file_name: "file1.pdf" , file_type: "1000" },
  { file: file2, file_name: "file2.pdf" , file_type: "2000" },
  { file: file3, file_name: "file3pdf" , file_type: "3000" },
];

files.forEach((item, index) => {
  formData.append(`file_${index}`, item.file); // 파일 추가
  formData.append(`filename_${index}`, item.filename); // 파일 이름 추가
});

// 목적을 추가로 FormData에 포함시킬 수 있습니다.
formData.append('purpose', 'examplePurpose');

// FormData를 서버에 전송 (예시로 axios 사용)
axios.post('/api/process-files', formData, {
  headers: {
    'Content-Type': 'multipart/form-data',
})
  .then(response => {
    console.log('Response:', response.data);
  })
  .catch(error => {
    console.error('Error:', error);
  });
