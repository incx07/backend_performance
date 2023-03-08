from flask import request
from flask_restful import Resource
from ...models.baselines import Baseline
from ...models.reports import Report
from ...connectors.minio_connector import MinioConnector


class API(Resource):
    url_params = [
        '<int:project_id>',
    ]

    def __init__(self, module):
        self.module = module

    def get(self, project_id: int):
        project = self.module.context.rpc_manager.call.project_get_or_404(project_id=project_id)
        baseline = Baseline.query.filter(
            Baseline.project_id == project.id,
            Baseline.test == request.args.get("test_name"),
            Baseline.environment == request.args.get("env")
        ).first()
        try:
            return {"baseline": baseline.summary, "report_id": baseline.report_id}, 200
        except AttributeError:
            return {"baseline": {}, "report_id": None}, 404

    def post(self, project_id: int):
        try:
            report_id = int(request.json['report_id'])
        except (KeyError, ValueError):
            return 'report_id must be provided', 400
        project = self.module.context.rpc_manager.call.project_get_or_404(project_id=project_id)
        report: Report = Report.query.filter(
            Report.project_id == project.id,
            Report.id == report_id
        ).first()
        if not report:
            return 'Not found', 404
        connector = MinioConnector(build_id=report.build_id, test_name=report.name)
        summary = connector.get_aggregated_test_results()
        
        baseline = Baseline(
            test=report.name,
            environment=report.environment,
            project_id=project.id,
            report_id=report.id,
            summary=summary
        )
        baseline.insert()
        return baseline.to_json(), 200
