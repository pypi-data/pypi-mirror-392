# SPDX-FileCopyrightText: © 2025 Josef Hahn
# SPDX-License-Identifier: AGPL-3.0-only
import klovve.driver

import annize.i18n
import annize.user_feedback


class UserFeedback(klovve.model.Model):

    annize_application: klovve.app.Application = klovve.model.property()

    feedback_tuples: list[tuple[int, klovve.views.interact.AbstractInteract]] = klovve.model.list_property()

    class __(klovve.model.ListTransformer):
        def output_item(self, item):
            return item[1]
    feedback_items: list[klovve.ui.View] = klovve.model.transformed_list_property(__(),
                                                                                  input_list_property=feedback_tuples)

    def _(self):
        return _UserFeedbackController(self)
    feedback_controller: "_UserFeedbackController" = klovve.model.computed_property(_)

    def handle_answered(self, interact: klovve.views.interact.AbstractInteract, answer: object) -> None:
        for i_tuple, (feedback_reqid, feedback_interact) in enumerate(self.feedback_tuples):
            if feedback_interact == interact:
                self.feedback_controller.set_answer(feedback_reqid, answer)
                self.feedback_tuples.pop(i_tuple)
                break


class _UserFeedbackController(annize.user_feedback.UserFeedbackController):

    def __init__(self, user_feedback: UserFeedback):
        self.__user_feedback = user_feedback
        self.__nextid = 0
        self.__requests = []  # TODO multithreading  ; cleanup  ; also for .__answers
        self.__answers = {}

    def __get_answer(self, request_id):
        while request_id not in self.__answers:
            pass
        return self.__answers.pop(request_id)

    def set_answer(self, request_id, answer):
        self.__answers[request_id] = answer

    def message_dialog(self, message, answers, config_key):
        request_id, self.__nextid = self.__nextid, self.__nextid + 1
        async def _():
            feedback_item = klovve.views.interact.Message(
                message=message + _UserFeedbackController.__automate_hint(config_key),
                choices=[(s, i) for i, s in enumerate(answers)])
            self.__user_feedback.feedback_tuples.append((request_id, feedback_item))
        klovve.driver.Driver.get().loop.enqueue(_())
        return self.__get_answer(request_id)

    def input_dialog(self, question, suggested_answer, config_key):
        request_id, self.__nextid = self.__nextid, self.__nextid + 1
        async def _():
            feedback_item = klovve.views.interact.TextInput(
                message=question + _UserFeedbackController.__automate_hint(config_key),
                suggestion=suggested_answer)
            self.__user_feedback.feedback_tuples.append((request_id, feedback_item))
        klovve.driver.Driver.get().loop.enqueue(_())
        return self.__get_answer(request_id)

    def choice_dialog(self, question, choices, config_key):
        request_id, self.__nextid = self.__nextid, self.__nextid + 1
        async def _():
            feedback_item = klovve.views.interact.Message(
                message=question + _UserFeedbackController.__automate_hint(config_key),
                choices=[*((s, i) for i, s in enumerate(choices)), (annize.i18n.tr("an_UI_cancel"), None)])
            self.__user_feedback.feedback_tuples.append((request_id, feedback_item))
        klovve.driver.Driver.get().loop.enqueue(_())
        return self.__get_answer(request_id)

    @staticmethod
    def __automate_hint(config_key: str|None) -> str:
        if not config_key:
            return ""
        return "\n\n" + annize.i18n.tr("an_UserFeedback_AnswerAutomatableByKey").format(config_key=config_key)
