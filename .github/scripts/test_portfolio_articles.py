import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
import export_portfolio_articles as exporter

class FeedTests(unittest.TestCase):
    def test_only_publishable_folders(self):
        for name in ['courses/topic/note.md', 'projects/Robot.md']:
            self.assertTrue(exporter.eligible(name))
        for name in ['01 Daily/day.md','templates/notes/Project.md','00 Inbox/draft.md','courses/img/drawing.excalidraw.md','projects/README.md','.obsidian/config.md','courses/.private/note.md','courses/notes.pdf','archive/course-bundles/old.md','research/note.md','guides/README.md','notebooks/README.md']:
            self.assertFalse(exporter.eligible(name), name)

    def test_stable_distinct_slugs(self):
        self.assertNotEqual(exporter.slug('courses/a/Intro.md'), exporter.slug('courses/b/Intro.md'))
        self.assertEqual(exporter.slug('projects/Robot.md'), exporter.slug('projects/Robot.md'))

    def test_folder_migration_preserves_article_urls(self):
        import hashlib
        for current, previous in exporter.LEGACY_ROOTS.items():
            old_path = previous + 'Example.md'
            new_path = current + 'Example.md'
            expected = 'dclab-example-' + hashlib.sha256(old_path.encode()).hexdigest()[:8]
            self.assertEqual(exporter.slug(new_path), expected)
            self.assertEqual(exporter.article_identity(new_path), old_path)
        self.assertEqual(exporter.article_identity('courses/new-topic/Example.md'),
                         'courses/new-topic/Example.md')

    def test_frontmatter_and_plain_notes(self):
        meta, body = exporter.metadata('---\ntitle: "My robot"\ndraft: true\ntags: [robotics, control]\n---\nText')
        self.assertEqual(meta['title'],'My robot')
        self.assertEqual(meta['draft'],'true')
        self.assertEqual(body,'Text')
        self.assertEqual(exporter.metadata('plain note'), ({}, 'plain note'))

    def test_obsidian_images_and_relative_links(self):
        source='courses/control/Timing.md'
        files={source,'courses/control/img/circuit.png','projects/Robot.md'}
        body=exporter.convert_links('![[circuit.png|400]]\n[[Robot|My robot]]\n[diagram](img/circuit.png)',source,files,{'projects/Robot.md'},'abc123')
        self.assertIn('![circuit](https://raw.githubusercontent.com/c-lydia/dclab_docs/abc123/courses/control/img/circuit.png)',body)
        self.assertIn('/#/articles/dclab-robot-',body)
        self.assertIn('https://github.com/c-lydia/dclab_docs/blob/abc123/',body)

    def test_code_and_external_links_unchanged(self):
        body='```cpp\n// ![[diagram.png]]\n```\n`[[Robot]]`\n[site](https://example.com)'
        self.assertEqual(exporter.convert_links(body,'projects/Robot.md',set(),set(),'abc'),body)

    def test_unknown_embeds_do_not_make_broken_images(self):
        self.assertEqual(exporter.convert_links('![[missing.png]]','projects/Robot.md',set(),set(),'abc'),'missing')

    def test_export_tracks_updates_removals_and_draft_opt_out(self):
        paths=['projects/Robot.md','courses/Draft.md']
        content={paths[0]:'# Robot\n\nVersion one',paths[1]:'---\ndraft: true\n---\nPrivate draft'}
        def fake_git(*args):
            return 'abc123' if args[0]=='rev-parse' else '2026-10-27T00:00:00Z\n2026-10-20T00:00:00Z'
        with patch.object(exporter,'git',side_effect=fake_git), patch.object(exporter.subprocess,'check_output',side_effect=lambda *a,**k:'\0'.join(paths).encode()), patch.object(Path,'read_text',autospec=True,side_effect=lambda p,**k:content[str(p)]):
            feed=exporter.build_feed()
            self.assertEqual(len(feed['articles']),1)
            article=feed['articles'][0]
            self.assertEqual(article['title'],'Robot')
            self.assertEqual(article['body'],'Version one')
            self.assertEqual(article['publishedAt'],'2026-10-20T00:00:00Z')
            content[paths[0]]='# Robot\n\nVersion two'
            self.assertEqual(exporter.build_feed()['articles'][0]['body'],'Version two')
            paths.pop(0)
            self.assertEqual(exporter.build_feed()['articles'],[])

if __name__=='__main__': unittest.main()
