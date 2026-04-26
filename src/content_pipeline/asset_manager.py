import json
from pathlib import Path

from .utils import slugify, today_str, ensure_dir


class AssetManager:
    def __init__(self, assets_dir: Path, output_dir: Path):
        self.assets_dir = assets_dir
        self.output_dir = output_dir
        self.topics_dir = assets_dir / "topics"

    def _topic_slug(self, topic: str) -> str:
        return f"{slugify(topic)}_{today_str()}"

    def save_input(self, topic: str, reference: str, platforms: list[str]) -> Path:
        """참고 자료를 에셋으로 저장"""
        slug = self._topic_slug(topic)
        topic_dir = ensure_dir(self.topics_dir / slug)

        # 참고 자료 저장
        input_file = topic_dir / "input.md"
        input_file.write_text(
            f"# {topic}\n\n## 참고 자료\n\n{reference}",
            encoding="utf-8",
        )

        # 메타데이터 저장
        metadata = {"topic": topic, "date": today_str(), "platforms": platforms}
        (topic_dir / "metadata.json").write_text(
            json.dumps(metadata, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )

        return topic_dir

    def save_output(self, topic: str, platform: str, content: str) -> Path:
        """생성된 콘텐츠를 출력 폴더에 저장"""
        slug = self._topic_slug(topic)
        output_dir = ensure_dir(self.output_dir / slug)
        output_file = output_dir / f"{platform}.md"
        output_file.write_text(content, encoding="utf-8")
        return output_file

    def list_topics(self) -> list[dict]:
        """저장된 토픽 목록 반환"""
        if not self.topics_dir.exists():
            return []
        results = []
        for d in sorted(self.topics_dir.iterdir()):
            meta_file = d / "metadata.json"
            if meta_file.exists():
                meta = json.loads(meta_file.read_text(encoding="utf-8"))
                meta["path"] = str(d)
                results.append(meta)
        return results

    def list_outputs(self) -> list[dict]:
        """생성된 출력 목록 반환"""
        if not self.output_dir.exists():
            return []
        results = []
        for d in sorted(self.output_dir.iterdir()):
            if d.is_dir():
                files = [f.stem for f in d.glob("*.md")]
                results.append({"slug": d.name, "platforms": files, "path": str(d)})
        return results

    def read_output(self, slug: str, platform: str) -> str | None:
        """특정 출력 파일 읽기"""
        target = self.output_dir / slug / f"{platform}.md"
        if target.exists():
            return target.read_text(encoding="utf-8")
        return None
