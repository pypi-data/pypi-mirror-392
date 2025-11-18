import duckrun
con = duckrun.connect("tmp/data.lakehouse/duck")
con.export_ducklake_to_delta("duck.db")
con.get_stats("summary")