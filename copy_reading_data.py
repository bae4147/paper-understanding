#!/usr/bin/env python3
"""
Firebase에서 reading 데이터 복사
소스: users/P004/experiments/session_1764994184869
타겟: users/P004/experiments/session_1764995452822
"""

import firebase_admin
from firebase_admin import credentials, firestore
import json

# Firebase 초기화
if not firebase_admin._apps:
    # 프로젝트 ID만으로 초기화 (Application Default Credentials 사용)
    firebase_admin.initialize_app(options={
        'projectId': 'paper-understanding',
    })

db = firestore.client()

def copy_reading_data():
    source_path = 'users/P004/experiments/session_1764994184869'
    target_path = 'users/P004/experiments/session_1764995452822'

    print('📖 Reading 데이터 복사 시작...')
    print(f'소스: {source_path}')
    print(f'타겟: {target_path}')
    print()

    try:
        # 1. 소스 문서에서 reading 필드 읽기
        source_ref = db.document(source_path)
        source_doc = source_ref.get()

        if not source_doc.exists:
            raise Exception('소스 문서를 찾을 수 없습니다.')

        source_data = source_doc.to_dict()
        reading_data = source_data.get('reading')

        if reading_data is None:
            raise Exception('소스 문서에 reading 필드가 없습니다.')

        print('✓ 소스 데이터 읽기 완료')
        print('Reading 데이터:')
        print(json.dumps(reading_data, indent=2, ensure_ascii=False))
        print()

        # 2. 타겟 문서의 reading 필드 덮어쓰기
        target_ref = db.document(target_path)

        # 타겟 문서 존재 확인
        target_doc = target_ref.get()
        if not target_doc.exists:
            raise Exception('타겟 문서를 찾을 수 없습니다.')

        # reading 필드만 업데이트
        target_ref.update({
            'reading': reading_data
        })

        print('✓ 타겟 문서 업데이트 완료')
        print()

        # 3. 확인
        updated_doc = target_ref.get()
        updated_data = updated_doc.to_dict()
        updated_reading = updated_data.get('reading')

        print('✓ 복사 완료!')
        print('업데이트된 reading 데이터:')
        print(json.dumps(updated_reading, indent=2, ensure_ascii=False))
        print()
        print('🎉 모든 작업이 완료되었습니다.')

    except Exception as e:
        print(f'❌ 오류 발생: {str(e)}')
        raise

if __name__ == '__main__':
    copy_reading_data()
