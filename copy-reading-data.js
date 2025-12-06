// Firebase Admin SDK를 사용하여 reading 데이터 복사
const admin = require('firebase-admin');

// Firebase 초기화
const serviceAccount = {
    "type": "service_account",
    "project_id": "paper-understanding",
    "private_key_id": process.env.FIREBASE_PRIVATE_KEY_ID,
    "private_key": process.env.FIREBASE_PRIVATE_KEY?.replace(/\\n/g, '\n'),
    "client_email": process.env.FIREBASE_CLIENT_EMAIL,
    "client_id": process.env.FIREBASE_CLIENT_ID,
    "auth_uri": "https://accounts.google.com/o/oauth2/auth",
    "token_uri": "https://oauth2.googleapis.com/token",
    "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
    "client_x509_cert_url": process.env.FIREBASE_CERT_URL
};

// 간단한 방법: 기존 Firebase 설정 사용
admin.initializeApp({
    credential: admin.credential.applicationDefault(),
    projectId: 'paper-understanding'
});

const db = admin.firestore();

async function copyReadingData() {
    const sourcePath = 'users/P004/experiments/session_1764994184869';
    const targetPath = 'users/P004/experiments/session_1764995452822';

    try {
        console.log('📖 Reading 데이터 복사 시작...');
        console.log(`소스: ${sourcePath}`);
        console.log(`타겟: ${targetPath}`);
        console.log('');

        // 1. 소스 문서에서 reading 필드 읽기
        const sourceDocRef = db.doc(sourcePath);
        const sourceDoc = await sourceDocRef.get();

        if (!sourceDoc.exists) {
            throw new Error('소스 문서를 찾을 수 없습니다.');
        }

        const sourceData = sourceDoc.data();
        const readingData = sourceData.reading;

        if (!readingData) {
            throw new Error('소스 문서에 reading 필드가 없습니다.');
        }

        console.log('✓ 소스 데이터 읽기 완료');
        console.log('Reading 데이터:', JSON.stringify(readingData, null, 2));
        console.log('');

        // 2. 타겟 문서의 reading 필드 덮어쓰기
        const targetDocRef = db.doc(targetPath);

        // 타겟 문서 존재 확인
        const targetDoc = await targetDocRef.get();
        if (!targetDoc.exists) {
            throw new Error('타겟 문서를 찾을 수 없습니다.');
        }

        await targetDocRef.update({
            reading: readingData
        });

        console.log('✓ 타겟 문서 업데이트 완료');
        console.log('');

        // 3. 확인
        const updatedDoc = await targetDocRef.get();
        const updatedData = updatedDoc.data();

        console.log('✓ 복사 완료!');
        console.log('업데이트된 reading 데이터:', JSON.stringify(updatedData.reading, null, 2));

    } catch (error) {
        console.error('❌ 오류 발생:', error.message);
        throw error;
    }
}

// 실행
copyReadingData()
    .then(() => {
        console.log('\n🎉 모든 작업이 완료되었습니다.');
        process.exit(0);
    })
    .catch((error) => {
        console.error('\n💥 작업 실패:', error);
        process.exit(1);
    });
