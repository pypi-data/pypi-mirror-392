import duckrun
def test_ducklake_export():
    con = duckrun.connect("tmp/tmp.Lakehouse/dbo")
    result = con.export_ducklake_to_delta("meta.db")
    return result
if __name__ == "__main__":
    test_ducklake_export()