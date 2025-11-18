from sqlthought import to_sql

def test_basic_query():
    print("Test started")

    result = to_sql(
        "List employee names with salary greater than 70000.",
        "tests/test.db"
    )

    print("Pipeline result:", result)

    assert result["success"] is True
    assert len(result["result"]) == 3




# import sys, os
# sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

# from sqlthought.pipeline import run_nlq_to_sql

# def test_basic_query():
#     print("🔥 Test started")

#     result = run_nlq_to_sql(
#         "List employee names with salary greater than 70000.",
#         "tests/test.db"
#     )

#     print("🔥 Pipeline result:", result)

#     assert "sql" in result
#     assert result["success"] is True
