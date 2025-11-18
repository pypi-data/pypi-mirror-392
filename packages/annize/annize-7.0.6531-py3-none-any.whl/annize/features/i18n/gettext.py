# SPDX-FileCopyrightText: © 2021 Josef Hahn
# SPDX-License-Identifier: AGPL-3.0-only
"""
gettext-based internationalization.
"""
import os
import subprocess

import annize.features.base
import annize.features.i18n.common
import annize.fs
import annize.i18n


class UpdatePOs:

    def __init__(self, *, po_directory: annize.fs.TInputPath):
        """
        :param po_directory: The directory with .po files.
        """
        self.__po_directory = annize.fs.content(po_directory)

    def __call__(self, *args, **kwargs):
        po_directory = self.__po_directory.path()
        project_directory = annize.features.base.project_directory()
        all_files = []
        for dir_tuple in os.walk(project_directory):
            for file_name in dir_tuple[2]:
                file = annize.fs.Path(f"{dir_tuple[0]}/{file_name}")
                if file.suffix in (".py", ".ui", ".xml", ".js", ".c", ".cpp", ".h", ".hpp"):
                    all_files.append(file)

        with annize.fs.fresh_temp_directory() as temp_dir:
            pot_file = temp_dir("pot.pot")
            files_file = temp_dir("files")
            files_file.write_text("\n".join(str(_) for _ in all_files))
            subprocess.check_call(("xgettext", "--keyword=tr", "--add-comments", "--from-code", "utf-8",
                                   "--sort-output", f"--files-from={files_file}", f"--output={pot_file}"))

            for po_file in {*po_directory.iterdir(),
                            *(po_directory(f"{culture.full_name}.po")
                              for culture in annize.features.i18n.common.project_cultures())}:
                if not po_file.suffix.lower() == ".po":
                    continue
                po_file.touch(exist_ok=True)
                subprocess.check_call(("msgmerge", "--no-fuzzy-matching", "--backup=none", "--update", po_file,
                                       pot_file))


class GenerateMOs:

    def __init__(self, *, po_directory: annize.fs.TFilesystemContent, mo_directory: annize.fs.TInputPath,
                 file_name: str|None):
        self.__po_directory = annize.fs.content(po_directory)
        self.__mo_directory = annize.fs.content(mo_directory)
        self.__file_name = file_name

    def __call__(self, *args, **kwargs):
        file_name = self.__file_name or annize.features.base.project_name()
        po_dir = self.__po_directory.path()
        mos_dir = self.__mo_directory.path()
        for po_file in po_dir.iterdir():
            if not po_file.suffix.lower() == ".po":
                continue
            out_dir = mos_dir / po_file.stem / "LC_MESSAGES"
            out_dir.mkdir(parents=True, exist_ok=True)
            subprocess.check_call(("msgfmt", f"--output-file={out_dir}/{file_name}.mo", po_file))


class TextSource:

    def __init__(self, *, mo_directory: annize.fs.TInputPath, priority: int = 0):
        mo_directory = annize.fs.content(mo_directory).path()
        annize.i18n.add_translation_provider(annize.i18n.GettextTranslationProvider(mo_directory), priority=priority)
